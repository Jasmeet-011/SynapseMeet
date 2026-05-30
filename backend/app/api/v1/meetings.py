"""Meeting endpoints — CRUD + live control."""

import time
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db, redis_client
from app.models.meeting import Meeting, MeetingStatus
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingOut, MeetingUpdate
from app.workers.tasks import process_meeting_audio

router = APIRouter()

# Local upload directory (used when GCS is not configured)
UPLOAD_DIR = Path("/tmp/synapsemeet_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AUDIO_TYPES = {
    "audio/webm", "audio/ogg", "audio/wav", "audio/mp4",
    "audio/mpeg", "audio/mp3", "video/webm",
}


@router.post("/", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = Meeting(
        title=payload.title,
        description=payload.description,
        language=payload.language,
        owner_id=current_user.id,
        workspace_id=current_user.workspace_id,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.get("/", response_model=list[MeetingOut])
async def list_meetings(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Meeting)
        .where(Meeting.owner_id == current_user.id)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_meeting(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingOut)
async def update_meeting(
    meeting_id: uuid.UUID,
    payload: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)

    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/start", response_model=MeetingOut)
async def start_meeting(
    meeting_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a meeting as LIVE — WebSocket gateway takes over from here."""
    from datetime import datetime, timezone

    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")

    meeting.status = MeetingStatus.LIVE
    meeting.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/end", response_model=MeetingOut)
async def end_meeting(
    meeting_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End meeting and enqueue AI processing pipeline."""
    from datetime import datetime, timezone

    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")

    meeting.status = MeetingStatus.PROCESSING
    meeting.ended_at = datetime.now(timezone.utc)
    if meeting.started_at:
        delta = meeting.ended_at - meeting.started_at
        meeting.duration_seconds = int(delta.total_seconds())

    await db.commit()
    await db.refresh(meeting)

    # Enqueue Celery task for post-meeting AI processing
    process_meeting_audio.delay(str(meeting_id))

    return meeting


@router.post("/{meeting_id}/transcribe-chunk")
async def transcribe_chunk(
    meeting_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receive a raw audio chunk from the WebSocket gateway and transcribe it via Whisper.
    Called internally by the gateway every 5 seconds during a live meeting.
    Appends the transcription to meeting.transcript and triggers a live summary.
    """
    audio_bytes = await request.body()
    if not audio_bytes:
        return {"transcript": ""}

    from app.services.transcription import transcribe_audio_chunk

    text = await transcribe_audio_chunk(audio_bytes)
    text = text.strip()

    if text:
        result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = result.scalar_one_or_none()
        if meeting:
            meeting.transcript = ((meeting.transcript or "") + " " + text).strip()
            await db.commit()

            # Throttle live summaries to at most once every 30 seconds
            throttle_key = f"last_summary_time:{meeting_id}"
            last_ts = await redis_client.get(throttle_key)
            now = time.time()
            if not last_ts or (now - float(last_ts)) >= 30:
                await redis_client.setex(throttle_key, 120, str(now))
                from app.workers.tasks import generate_live_summary
                generate_live_summary.delay(str(meeting_id), meeting.transcript)

    return {"transcript": text}


@router.post("/{meeting_id}/upload-audio", status_code=status.HTTP_202_ACCEPTED)
async def upload_audio(
    meeting_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a pre-recorded audio file for async transcription + AI processing."""
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")

    content_type = file.content_type or ""
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported audio type: {content_type}. Allowed: {', '.join(ALLOWED_AUDIO_TYPES)}",
        )

    # Save file locally (swap for GCS upload when GCS_BUCKET_NAME is configured)
    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    dest = UPLOAD_DIR / f"{meeting_id}{suffix}"
    contents = await file.read()
    dest.write_bytes(contents)

    meeting.audio_url = str(dest)
    meeting.status = MeetingStatus.PROCESSING
    await db.commit()

    # Celery task handles full transcription + AI pipeline
    from app.workers.tasks import process_uploaded_audio
    process_uploaded_audio.delay(str(meeting_id), str(dest))

    return {"message": "Audio upload accepted, processing queued", "meeting_id": str(meeting_id)}

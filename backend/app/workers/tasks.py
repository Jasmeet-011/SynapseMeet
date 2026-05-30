"""Celery tasks — AI processing pipeline."""

import asyncio
import json
import uuid

from app.workers.celery_app import celery_app


def run_async(coro):
    """Helper to run async code inside synchronous Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ─── process_meeting_audio ────────────────────────────────────────────────────

@celery_app.task(name="app.workers.tasks.process_meeting_audio", bind=True, max_retries=3)
def process_meeting_audio(self, meeting_id: str):
    """
    Full post-meeting AI pipeline:
    1. Speaker diarization (AssemblyAI — skipped if no public audio_url or no API key)
    2. Summarize transcript (GPT-4o)
    3. Extract action items (GPT-4o function calling)
    4. Extract topics + keywords
    5. Sentiment analysis
    6. Index in Pinecone for search
    7. Save action items to DB + publish to Redis
    8. Update knowledge graph (Neo4j)
    9. Sync to integrations (Slack)
    """
    try:
        run_async(_process_meeting_pipeline(meeting_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


async def _process_meeting_pipeline(meeting_id: str):
    from sqlalchemy import select

    from app.core.config import settings
    from app.core.database import AsyncSessionLocal, neo4j_driver, redis_client
    from app.models.action_item import ActionItem
    from app.models.meeting import Meeting, MeetingStatus
    from app.services.search import index_meeting
    from app.services.summarization import (
        analyze_sentiment,
        extract_action_items,
        extract_topics_and_keywords,
        generate_summary,
    )

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meeting).where(Meeting.id == uuid.UUID(meeting_id)))
        meeting = result.scalar_one_or_none()
        if not meeting or not meeting.transcript:
            return

        try:
            # 1. Speaker diarization — only when a public audio URL + API key are available
            if (
                meeting.audio_url
                and meeting.audio_url.startswith("http")
                and settings.ASSEMBLYAI_API_KEY
            ):
                try:
                    from app.services.transcription import diarize_audio
                    utterances = await diarize_audio(meeting.audio_url)
                    if utterances:
                        speakers = {
                            utt["speaker"]: f"Speaker {utt['speaker']}"
                            for utt in utterances
                        }
                        meeting.speakers = speakers
                except Exception as e:
                    print(f"[Pipeline] Diarization failed (non-critical): {e}")

            # 2. Generate summary
            summary = await generate_summary(meeting.transcript, meeting.language)
            meeting.summary = summary

            # 3. Extract action items
            action_items_data = await extract_action_items(meeting.transcript)

            # 4. Topics + keywords
            extracted = await extract_topics_and_keywords(meeting.transcript)
            meeting.topics = extracted.get("topics", [])
            meeting.keywords = extracted.get("keywords", [])

            # 5. Sentiment analysis
            if meeting.speakers:
                meeting.sentiment_data = await analyze_sentiment(
                    meeting.transcript, meeting.speakers
                )

            meeting.status = MeetingStatus.COMPLETED
            await db.commit()

            # 6. Index in Pinecone (non-critical)
            try:
                await index_meeting(
                    meeting_id=meeting_id,
                    title=meeting.title,
                    content=f"{summary}\n{meeting.transcript[:2000]}",
                    metadata={
                        "user_id": str(meeting.owner_id),
                        "workspace_id": str(meeting.workspace_id) if meeting.workspace_id else "",
                        "created_at": meeting.created_at.isoformat(),
                    },
                )
            except Exception as e:
                print(f"[Pipeline] Pinecone indexing failed (non-critical): {e}")

            # 7. Save action items to DB + broadcast via Redis pub/sub
            for item_data in action_items_data:
                item = ActionItem(
                    meeting_id=meeting.id,
                    title=item_data["title"],
                    assignee_name=item_data.get("assignee_name"),
                    priority=item_data.get("priority", "medium"),
                    transcript_excerpt=item_data.get("transcript_excerpt"),
                )
                db.add(item)
                await redis_client.publish(
                    "meeting:action_item",
                    json.dumps({
                        "meetingId": meeting_id,
                        "item": {
                            "title": item_data["title"],
                            "assignee_name": item_data.get("assignee_name"),
                            "priority": item_data.get("priority", "medium"),
                            "transcript_excerpt": item_data.get("transcript_excerpt"),
                        },
                    }),
                )
            await db.commit()

            # 8. Update Neo4j knowledge graph (non-critical)
            try:
                from app.services.knowledge_graph import (
                    link_person_to_meeting,
                    link_topic_to_meeting,
                    upsert_meeting_node,
                    upsert_person_node,
                    upsert_topic_node,
                )

                async with neo4j_driver.session() as neo4j_session:
                    await upsert_meeting_node(
                        neo4j_session,
                        meeting_id,
                        meeting.title,
                        meeting.created_at.date().isoformat(),
                    )
                    for topic in (meeting.topics or []):
                        await upsert_topic_node(neo4j_session, topic)
                        await link_topic_to_meeting(neo4j_session, topic, meeting_id)

                    assignees = {
                        item_data["assignee_name"]
                        for item_data in action_items_data
                        if item_data.get("assignee_name")
                    }
                    for assignee in assignees:
                        await upsert_person_node(neo4j_session, assignee)
                        await link_person_to_meeting(neo4j_session, assignee, meeting_id)
            except Exception as e:
                print(f"[Pipeline] Neo4j update failed (non-critical): {e}")

            # 9. Kick off integration sync (Slack, etc.)
            sync_integrations.delay(meeting_id, {})

        except Exception as exc:
            meeting.status = MeetingStatus.FAILED
            await db.commit()
            raise


# ─── process_uploaded_audio ───────────────────────────────────────────────────

@celery_app.task(name="app.workers.tasks.process_uploaded_audio", bind=True, max_retries=3)
def process_uploaded_audio(self, meeting_id: str, audio_path: str):
    """
    Transcribe an uploaded audio file with Whisper, then run the full AI pipeline.
    Called by POST /meetings/{id}/upload-audio.
    """
    try:
        run_async(_transcribe_and_process(meeting_id, audio_path))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


async def _transcribe_and_process(meeting_id: str, audio_path: str):
    from pathlib import Path
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.meeting import Meeting, MeetingStatus
    from app.services.transcription import transcribe_audio

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meeting).where(Meeting.id == uuid.UUID(meeting_id)))
        meeting = result.scalar_one_or_none()
        if not meeting:
            return

        try:
            result_data = await transcribe_audio(audio_path)
            meeting.transcript = result_data["text"]
            meeting.language = result_data.get("language") or meeting.language
            await db.commit()
        except Exception as exc:
            meeting.status = MeetingStatus.FAILED
            await db.commit()
            raise

    # Clean up local file after successful transcription
    try:
        Path(audio_path).unlink(missing_ok=True)
    except Exception:
        pass

    # Full AI pipeline (uses its own DB session)
    await _process_meeting_pipeline(meeting_id)


# ─── generate_live_summary ────────────────────────────────────────────────────

@celery_app.task(name="app.workers.tasks.generate_live_summary")
def generate_live_summary(meeting_id: str, transcript_so_far: str):
    """Generate a rolling summary during a live meeting (throttled to ~30s intervals)."""
    run_async(_live_summary(meeting_id, transcript_so_far))


async def _live_summary(meeting_id: str, transcript_so_far: str):
    from app.core.database import redis_client
    from app.services.summarization import generate_summary

    if not transcript_so_far.strip():
        return

    summary = await generate_summary(transcript_so_far)

    # Cache for on-demand retrieval (request_summary socket event)
    await redis_client.setex(f"live_summary:{meeting_id}", 120, summary)

    # Publish to Redis channel — gateway fan-outs to all meeting participants
    await redis_client.publish(
        "meeting:summary",
        json.dumps({"meetingId": meeting_id, "summary": summary}),
    )


# ─── sync_integrations ────────────────────────────────────────────────────────

@celery_app.task(name="app.workers.tasks.sync_integrations")
def sync_integrations(meeting_id: str, channels: dict):
    """Push meeting summary + action items to Slack (and future integrations) post-meeting."""
    run_async(_sync(meeting_id, channels))


async def _sync(meeting_id: str, channels: dict):
    from sqlalchemy import select

    from app.core.config import settings
    from app.core.database import AsyncSessionLocal
    from app.models.action_item import ActionItem
    from app.models.meeting import Meeting
    from app.services.integrations import push_action_items_to_slack

    if not settings.SLACK_BOT_TOKEN:
        return

    slack_channel = channels.get("slack") or settings.SLACK_DEFAULT_CHANNEL
    if not slack_channel:
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Meeting).where(Meeting.id == uuid.UUID(meeting_id)))
        meeting = result.scalar_one_or_none()
        if not meeting:
            return

        items_result = await db.execute(
            select(ActionItem).where(ActionItem.meeting_id == meeting.id)
        )
        action_items = items_result.scalars().all()

        if not action_items:
            return

        items_list = [
            {
                "title": item.title,
                "assignee_name": item.assignee_name,
                "due_date": item.due_date.isoformat() if item.due_date else None,
            }
            for item in action_items
        ]

        try:
            await push_action_items_to_slack(meeting.title, items_list, slack_channel)
        except Exception as e:
            print(f"[Sync] Slack push failed for meeting {meeting_id}: {e}")

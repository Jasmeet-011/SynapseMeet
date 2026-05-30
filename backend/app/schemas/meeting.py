"""Meeting Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.meeting import MeetingStatus


class MeetingCreate(BaseModel):
    title: str
    description: str | None = None
    language: str = "en"


class MeetingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: MeetingStatus | None = None


class MeetingOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    owner_id: uuid.UUID
    status: MeetingStatus
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None
    summary: str | None
    language: str
    speakers: dict | None
    topics: list | None
    keywords: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LiveSummaryOut(BaseModel):
    meeting_id: uuid.UUID
    summary: str
    action_items_count: int
    timestamp: datetime

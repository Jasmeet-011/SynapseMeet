"""Action item Pydantic schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.action_item import ActionItemPriority, ActionItemStatus


class ActionItemCreate(BaseModel):
    meeting_id: uuid.UUID
    title: str
    description: str | None = None
    assignee_name: str | None = None
    priority: ActionItemPriority = ActionItemPriority.MEDIUM
    due_date: date | None = None
    transcript_excerpt: str | None = None
    timestamp_seconds: float | None = None


class ActionItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ActionItemStatus | None = None
    priority: ActionItemPriority | None = None
    due_date: date | None = None
    assignee_id: uuid.UUID | None = None
    assignee_name: str | None = None


class ActionItemOut(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    title: str
    description: str | None
    assignee_name: str | None
    status: ActionItemStatus
    priority: ActionItemPriority
    due_date: date | None
    jira_issue_id: str | None
    notion_page_id: str | None
    transcript_excerpt: str | None
    timestamp_seconds: float | None
    created_at: datetime

    model_config = {"from_attributes": True}

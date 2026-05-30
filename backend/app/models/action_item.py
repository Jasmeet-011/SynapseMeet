"""Action item model — extracted from meeting transcripts."""

import uuid
from datetime import date, datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActionItemStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class ActionItemPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Assignee (parsed from transcript — may be a name string if not a registered user)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    assignee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ActionItemStatus] = mapped_column(
        Enum(ActionItemStatus), default=ActionItemStatus.PENDING
    )
    priority: Mapped[ActionItemPriority] = mapped_column(
        Enum(ActionItemPriority), default=ActionItemPriority.MEDIUM
    )

    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # External sync
    jira_issue_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notion_page_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    slack_message_ts: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Transcript context (where it was mentioned)
    transcript_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp_seconds: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="action_items")  # noqa: F821

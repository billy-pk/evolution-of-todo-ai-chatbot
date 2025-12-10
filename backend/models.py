from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task model for database table.
    Represents a todo item belonging to a specific user.
    """
    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )

    user_id: str = Field(
        index=True,
        max_length=255,
        description="User ID from Better Auth"
    )

    title: str = Field(
        max_length=200,
        min_length=1,
        description="Task title (required)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )

    completed: bool = Field(
        default=False,
        description="Completion status"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last update timestamp (UTC)"
    )
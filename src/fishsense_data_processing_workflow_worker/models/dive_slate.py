"""SQLModel model for DiveSlate table."""

from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel


class DiveSlate(SQLModel, table=True):
    """Model representing a dive slate."""

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    path: str = Field(max_length=255, unique=True, index=True)
    created_at: datetime | None = Field(
        sa_type=DateTime(timezone=True), default_factory=datetime.utcnow
    )

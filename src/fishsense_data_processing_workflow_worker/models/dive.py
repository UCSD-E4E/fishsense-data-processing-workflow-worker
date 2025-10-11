"""Model representing a dive."""

from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel

from fishsense_data_processing_workflow_worker.models.priority import Priority


class Dive(SQLModel, table=True):
    """Model representing a dive."""

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, index=True)
    path: str = Field(max_length=255, unique=True, index=True)
    dive_datetime: datetime = Field(sa_type=DateTime(timezone=True), default=None)
    priority: Priority = Field(default=Priority.LOW, index=True)
    flip_dive_slate: bool | None = Field(default=False)

    camera_id: int | None = Field(default=None, foreign_key="camera.id")
    dive_slate_id: int | None = Field(default=None, foreign_key="diveslate.id")

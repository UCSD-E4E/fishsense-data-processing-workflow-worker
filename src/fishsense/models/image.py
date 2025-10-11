"""Model representing an image."""

from datetime import datetime

from sqlmodel import DateTime, Field, SQLModel


class Image(SQLModel, table=True):
    """Model representing an image."""

    id: int | None = Field(default=None, primary_key=True)
    path: str = Field(max_length=255, unique=True, index=True)
    taken_datetime: datetime = Field(sa_type=DateTime(timezone=True), default=None)
    checksum: str = Field(max_length=32, index=True)
    is_canonical: bool = Field(default=False)

    dive_id: int | None = Field(default=None, foreign_key="dive.id")
    camera_id: int | None = Field(default=None, foreign_key="camera.id")

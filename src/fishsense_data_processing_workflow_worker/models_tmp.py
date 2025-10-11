from datetime import datetime

from pydantic import BaseModel


class Dive(BaseModel):
    """Model representing a dive."""

    id: int | None
    name: str | None
    path: str
    dive_datetime: datetime
    priority: str
    flip_dive_slate: bool | None

    camera_id: int | None
    dive_slate_id: int | None


class Image(BaseModel):
    """Model representing an image."""

    id: int | None
    path: str | None
    taken_datetime: datetime | None
    checksum: str | None
    is_canonical: bool | None

    dive_id: int | None
    camera_id: int | None
    dive_id: int | None
    camera_id: int | None

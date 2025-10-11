"""Model representing a camera."""

from sqlmodel import Field, SQLModel


class Camera(SQLModel, table=True):
    """Model representing a camera."""

    id: int | None = Field(default=None, primary_key=True)
    serial_number: str = Field(unique=True, index=True)
    name: str = Field(unique=True, index=True)

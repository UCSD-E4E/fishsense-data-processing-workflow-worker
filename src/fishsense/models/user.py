"""Model representing a user."""

from __future__ import annotations

from datetime import datetime
from typing import Self

from sqlmodel import DateTime, Field, SQLModel


class User(SQLModel, table=True):
    """Model representing a user."""

    id: int | None = Field(default=None, primary_key=True)
    label_studio_id: int | None = Field(default=None, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    last_activity: datetime | None = Field(
        sa_type=DateTime(timezone=True), default=None
    )
    date_joined: datetime | None = Field(sa_type=DateTime(timezone=True), default=None)

    @classmethod
    def from_label_studio(cls, user) -> Self:
        """Create a User instance from a Label Studio user."""

        from label_studio_sdk import (  # pylint: disable=import-outside-toplevel
            LseUserApi,
        )

        user: LseUserApi = user

        return cls(
            label_studio_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            last_activity=user.last_activity,
            date_joined=user.date_joined,
        )

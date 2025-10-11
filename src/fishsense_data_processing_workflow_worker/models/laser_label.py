"""Model representing a laser label from Label Studio."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Self

from sqlmodel import JSON, Column, DateTime, Field, SQLModel

from fishsense_data_processing_workflow_worker.models.label_studio_label_base import (
    LabelStudioLabelBase,
)


class LaserLabel(LabelStudioLabelBase, SQLModel, table=True):
    # pylint: disable=duplicate-code
    """Model representing a laser label."""

    id: int | None = Field(default=None, primary_key=True)
    label_studio_task_id: int | None = Field(default=None, unique=True, index=True)
    x: float | None = Field(default=None)
    y: float | None = Field(default=None)
    label: str | None = Field(default=None)
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True), default=None)
    completed: bool | None = Field(default=False)
    label_studio_json: Dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON)
    )

    image_id: int | None = Field(default=None, foreign_key="image.id")
    user_id: int | None = Field(default=None, foreign_key="user.id")

    @classmethod
    def from_task(cls, task: Any) -> Self:
        """Create a LaserLabel instance from a Label Studio task."""

        log = logging.getLogger("LaserLabel")
        log.debug("Initializing LaserLabel with task ID: %s", task.id)

        return cls(
            label_studio_task_id=task.id,
            x=cls.__parse_x_y(task)[0],
            y=cls.__parse_x_y(task)[1],
            label=cls.__parse_label(task),
            updated_at=cls.__parse_updated_time(task),
            completed=cls.label_studio_task_has_result(task),
            label_studio_json=json.loads(task.json()),
        )

    @staticmethod
    def __parse_x_y(task: Any) -> tuple[int, int]:
        if LaserLabel.label_studio_task_has_result(task) is False:
            return None, None

        log = logging.getLogger("LaserLabel")
        original_width = task.annotations[0]["result"][0]["original_width"]
        original_height = task.annotations[0]["result"][0]["original_height"]

        log.debug(
            "Parsed original height and width: %s, %s", original_width, original_height
        )

        x = int(
            round(task.annotations[0]["result"][0]["value"]["x"] * original_width / 100)
        )
        y = int(
            round(
                task.annotations[0]["result"][0]["value"]["y"] * original_height / 100
            )
        )

        log.debug("Parsed coordinates: x=%s, y=%s", x, y)

        return x, y

    @staticmethod
    def __parse_label(task: Any) -> str:
        if LaserLabel.label_studio_task_has_result(task) is False:
            return None

        log = logging.getLogger("LaserLabel")
        label = task.annotations[0]["result"][0]["value"]["keypointlabels"][0]

        log.debug("Parsed label: %s", label)

        return label

    @staticmethod
    def __parse_updated_time(task: Any) -> datetime | None:
        log = logging.getLogger("LaserLabel")
        updated_at = datetime.fromisoformat(task.annotations[0]["updated_at"])

        log.debug("Parsed updated_at: %s", updated_at)

        return updated_at

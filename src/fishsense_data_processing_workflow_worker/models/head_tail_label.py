"""This module defines the HeadTailLabel model, which represents a head-tail label"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Self

from sqlmodel import JSON, Column, DateTime, Field, SQLModel

from fishsense_data_processing_workflow_worker.models.label_studio_label_base import (
    LabelStudioLabelBase,
)


class HeadTailLabel(LabelStudioLabelBase, SQLModel, table=True):
    # pylint: disable=duplicate-code
    """Model representing a head-tail label."""

    id: int | None = Field(default=None, primary_key=True)
    label_studio_task_id: int | None = Field(default=None, unique=True, index=True)
    head_x: float | None = Field(default=None)
    head_y: float | None = Field(default=None)
    tail_x: float | None = Field(default=None)
    tail_y: float | None = Field(default=None)
    updated_at: datetime | None = Field(sa_type=DateTime(timezone=True), default=None)
    completed: bool | None = Field(default=False)
    label_studio_json: Dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON)
    )

    image_id: int | None = Field(default=None, foreign_key="image.id")
    user_id: int | None = Field(default=None, foreign_key="user.id")

    @classmethod
    def from_task(cls, task: Any) -> Self:
        """Create a HeadTailLabel instance from a Label Studio task."""

        log = logging.getLogger("HeadTailLabel")
        log.debug("Initializing HeadTailLabel with task ID: %s", task.id)

        return cls(
            label_studio_task_id=task.id,
            head_x=cls.__parse_x_y(task, "Snout")[0],
            head_y=cls.__parse_x_y(task, "Snout")[1],
            tail_x=cls.__parse_x_y(task, "Fork")[0],
            tail_y=cls.__parse_x_y(task, "Fork")[1],
            updated_at=cls.__parse_updated_time(task),
            completed=cls.label_studio_task_has_result(task),
            label_studio_json=json.loads(task.json()),
        )

    @staticmethod
    def __parse_x_y(task: Any, label: str) -> tuple[int | None, int | None]:
        if HeadTailLabel.label_studio_task_has_result(task) is False:
            return None, None

        label_value = [
            result
            for result in task.annotations[0]["result"]
            if label in result["value"]["keypointlabels"]
        ][0]

        log = logging.getLogger("HeadTailLabel")
        original_width = label_value["original_width"]
        original_height = label_value["original_height"]

        log.debug(
            "Parsed original height and width: %s, %s", original_width, original_height
        )

        x = int(round(label_value["value"]["x"] * original_width / 100))
        y = int(round(label_value["value"]["y"] * original_height / 100))

        log.debug("Parsed coordinates: x=%s, y=%s", x, y)

        return x, y

    @staticmethod
    def __parse_updated_time(task: Any) -> datetime | None:
        log = logging.getLogger("LaserLabel")
        updated_at = datetime.fromisoformat(task.annotations[0]["updated_at"])

        log.debug("Parsed updated_at: %s", updated_at)

        return updated_at

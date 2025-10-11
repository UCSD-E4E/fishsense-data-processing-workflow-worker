"""Base class for Label Studio label models."""

from __future__ import annotations

from typing import Any, Self


class LabelStudioLabelBase:
    """Base class for Label Studio label models."""

    @classmethod
    def from_task(cls, task: Any) -> Self:
        """Create a LabelStudioLabelBase instance from a Label Studio task."""
        raise NotImplementedError("Subclasses must implement this method.")

    @staticmethod
    def label_studio_task_has_result(task: Any) -> bool:
        """Check if a Label Studio task has results."""
        return bool(task.annotations and task.annotations[0]["result"])

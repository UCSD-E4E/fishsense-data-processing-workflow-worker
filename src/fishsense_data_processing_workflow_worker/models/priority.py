"""Module defining the Priority enumeration."""

from enum import Enum


class Priority(str, Enum):
    """Enumeration for priority levels."""

    LOW = "LOW"
    HIGH = "HIGH"

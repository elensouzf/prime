"""Domain models for task management."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, Optional

_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class TaskStatus(str, Enum):
    """Available states for a task."""

    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(slots=True)
class Task:
    """Represents a task tracked by the assistant."""

    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = field(default_factory=lambda: datetime.utcnow())
    reminder_time: Optional[time] = None

    def mark_completed(self) -> None:
        """Mark the task as completed and refresh the ``updated_at`` timestamp."""

        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def set_reminder_time(self, reminder_time: Optional[time]) -> None:
        """Attach or remove a reminder time to the task."""

        self.reminder_time = reminder_time
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task into a JSON-friendly structure."""

        payload: Dict[str, Any] = {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.strftime(_ISO_FORMAT),
            "updated_at": self.updated_at.strftime(_ISO_FORMAT),
        }
        if self.reminder_time is not None:
            payload["reminder_time"] = self.reminder_time.strftime("%H:%M")
        return payload

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Task":
        """Build a :class:`Task` from serialized data."""

        created_at = datetime.strptime(payload["created_at"], _ISO_FORMAT)
        updated_at = datetime.strptime(payload["updated_at"], _ISO_FORMAT)
        reminder_time: Optional[time] = None
        if "reminder_time" in payload and payload["reminder_time"] is not None:
            reminder_time = time.fromisoformat(payload["reminder_time"])
        return cls(
            id=int(payload["id"]),
            description=str(payload["description"]),
            status=TaskStatus(payload["status"]),
            created_at=created_at,
            updated_at=updated_at,
            reminder_time=reminder_time,
        )


@dataclass(slots=True)
class ReminderConfirmation:
    """Represents a pending confirmation to attach a reminder to a task."""

    id: str
    task_id: int
    reminder_time: time
    prompt: str
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "reminder_time": self.reminder_time.strftime("%H:%M"),
            "prompt": self.prompt,
            "created_at": self.created_at.strftime(_ISO_FORMAT),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ReminderConfirmation":
        return cls(
            id=str(payload["id"]),
            task_id=int(payload["task_id"]),
            reminder_time=time.fromisoformat(payload["reminder_time"]),
            prompt=str(payload["prompt"]),
            created_at=datetime.strptime(payload["created_at"], _ISO_FORMAT),
        )


__all__ = ["ReminderConfirmation", "Task", "TaskStatus"]

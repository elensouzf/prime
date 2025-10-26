"""Persistence layer for tasks and confirmations."""
from __future__ import annotations

import json
from datetime import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from .models import ReminderConfirmation, Task


class TaskRepository:
    """Simple JSON-backed repository for tasks and confirmations."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.tasks_file = base_path / "tasks.json"
        self.confirmations_file = base_path / "confirmations.json"
        self.base_path.mkdir(parents=True, exist_ok=True)
        if not self.tasks_file.exists():
            self._write_tasks({"next_id": 1, "tasks": []})
        if not self.confirmations_file.exists():
            self._write_confirmations({"confirmations": []})

    # ------------------------------------------------------------------
    # Private helpers
    def _read_tasks(self) -> Dict[str, object]:
        with self.tasks_file.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def _write_tasks(self, payload: Dict[str, object]) -> None:
        with self.tasks_file.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    def _read_confirmations(self) -> Dict[str, object]:
        with self.confirmations_file.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def _write_confirmations(self, payload: Dict[str, object]) -> None:
        with self.confirmations_file.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Tasks
    def _next_id(self, state: Dict[str, object]) -> int:
        next_id = int(state.get("next_id", 1))
        state["next_id"] = next_id + 1
        return next_id

    def add_task(self, description: str) -> Task:
        state = self._read_tasks()
        task = Task(id=self._next_id(state), description=description)
        tasks = [Task.from_dict(item) for item in state.get("tasks", [])]
        tasks.append(task)
        state["tasks"] = [t.to_dict() for t in tasks]
        self._write_tasks(state)
        return task

    def list_tasks(self) -> List[Task]:
        state = self._read_tasks()
        return [Task.from_dict(item) for item in state.get("tasks", [])]

    def update_task(self, task: Task) -> None:
        state = self._read_tasks()
        tasks = [Task.from_dict(item) for item in state.get("tasks", [])]
        for idx, existing in enumerate(tasks):
            if existing.id == task.id:
                tasks[idx] = task
                break
        else:
            raise KeyError(f"Task {task.id} not found")
        state["tasks"] = [t.to_dict() for t in tasks]
        self._write_tasks(state)

    def get_task(self, task_id: int) -> Task:
        for task in self.list_tasks():
            if task.id == task_id:
                return task
        raise KeyError(f"Task {task_id} not found")

    def complete_task(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        task.mark_completed()
        self.update_task(task)
        return task

    def set_task_reminder(self, task_id: int, reminder_time: Optional[time]) -> Task:
        task = self.get_task(task_id)
        task.set_reminder_time(reminder_time)
        self.update_task(task)
        return task

    # ------------------------------------------------------------------
    # Confirmations
    def create_reminder_confirmation(self, task_id: int, reminder_time: time, prompt: Optional[str] = None) -> ReminderConfirmation:
        confirmation = ReminderConfirmation(
            id=str(uuid4()),
            task_id=task_id,
            reminder_time=reminder_time,
            prompt=prompt
            or f"Deseja que eu lembre às {format_time_for_speech(reminder_time)}?",
        )
        state = self._read_confirmations()
        confirmations = [ReminderConfirmation.from_dict(item) for item in state.get("confirmations", [])]
        confirmations.append(confirmation)
        state["confirmations"] = [item.to_dict() for item in confirmations]
        self._write_confirmations(state)
        return confirmation

    def list_confirmations(self) -> Iterable[ReminderConfirmation]:
        state = self._read_confirmations()
        return [ReminderConfirmation.from_dict(item) for item in state.get("confirmations", [])]

    def get_confirmation(self, confirmation_id: str) -> ReminderConfirmation:
        for confirmation in self.list_confirmations():
            if confirmation.id == confirmation_id:
                return confirmation
        raise KeyError(f"Confirmation {confirmation_id} not found")

    def remove_confirmation(self, confirmation_id: str) -> None:
        state = self._read_confirmations()
        confirmations = [ReminderConfirmation.from_dict(item) for item in state.get("confirmations", [])]
        confirmations = [item for item in confirmations if item.id != confirmation_id]
        state["confirmations"] = [item.to_dict() for item in confirmations]
        self._write_confirmations(state)


def format_time_for_speech(reminder_time: time) -> str:
    """Format a time in a natural language friendly way."""

    minutes = reminder_time.minute
    hour = reminder_time.hour
    if minutes == 0:
        return f"{hour}h"
    return f"{hour}h{minutes:02d}"


__all__ = ["TaskRepository", "format_time_for_speech"]

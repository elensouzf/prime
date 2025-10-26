"""Intent handlers for the conversational assistant."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Optional

from .models import ReminderConfirmation
from .storage import TaskRepository, format_time_for_speech


@dataclass(slots=True)
class HandlerResult:
    """Represents the outcome of an intent handler."""

    message: str
    confirmation: Optional[ReminderConfirmation] = None


def handle_listar_tarefas(repository: TaskRepository) -> HandlerResult:
    """Produce a human-friendly summary of the stored tasks."""

    tasks = repository.list_tasks()
    if not tasks:
        return HandlerResult("Você ainda não tem tarefas na sua lista.")

    pending = [task for task in tasks if task.status.value == "pending"]
    completed = [task for task in tasks if task.status.value == "completed"]

    segments = []
    if pending:
        formatted = ", ".join(
            f"#{task.id} '{task.description}'"
            + (
                f" com lembrete às {format_time_for_speech(task.reminder_time)}"
                if task.reminder_time
                else ""
            )
            for task in pending
        )
        segments.append(
            "Tarefas pendentes: " + formatted + "."
        )
    if completed:
        formatted = ", ".join(f"#{task.id} '{task.description}'" for task in completed)
        segments.append("Concluídas: " + formatted + ".")

    return HandlerResult(" ".join(segments))


def handle_adicionar_tarefa(
    repository: TaskRepository,
    description: str,
    reminder_time: Optional[time] = None,
    require_confirmation: bool = False,
) -> HandlerResult:
    """Create a new task and optionally request confirmation for a reminder."""

    task = repository.add_task(description)
    base_message = f"Adicionei a tarefa #{task.id} '{task.description}'."
    if reminder_time is None:
        return HandlerResult(base_message)

    if require_confirmation:
        confirmation = repository.create_reminder_confirmation(task.id, reminder_time)
        message = base_message + " " + confirmation.prompt
        return HandlerResult(message, confirmation=confirmation)

    repository.set_task_reminder(task.id, reminder_time)
    message = (
        base_message
        + f" Vou te lembrar às {format_time_for_speech(reminder_time)}."
    )
    return HandlerResult(message)


def handle_concluir_tarefa(repository: TaskRepository, task_id: int) -> HandlerResult:
    """Mark a task as completed and craft a friendly response."""

    task = repository.complete_task(task_id)
    message = f"A tarefa #{task.id} '{task.description}' está concluída. Bom trabalho!"
    return HandlerResult(message)


def handle_confirmar_lembrete(
    repository: TaskRepository,
    confirmation_id: str,
    accepted: bool,
) -> HandlerResult:
    """Apply or discard a pending reminder confirmation."""

    confirmation = repository.get_confirmation(confirmation_id)
    repository.remove_confirmation(confirmation_id)

    if not accepted:
        message = (
            f"Tudo bem, não vou adicionar o lembrete das {format_time_for_speech(confirmation.reminder_time)}."
        )
        return HandlerResult(message)

    repository.set_task_reminder(confirmation.task_id, confirmation.reminder_time)
    message = (
        f"Perfeito! Vou lembrar da tarefa #{confirmation.task_id} às {format_time_for_speech(confirmation.reminder_time)}."
    )
    return HandlerResult(message)


__all__ = [
    "HandlerResult",
    "handle_adicionar_tarefa",
    "handle_confirmar_lembrete",
    "handle_concluir_tarefa",
    "handle_listar_tarefas",
]

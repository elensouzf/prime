from __future__ import annotations

from datetime import time
from pathlib import Path

import pytest

from assistant.handlers import (
    handle_adicionar_tarefa,
    handle_confirmar_lembrete,
    handle_concluir_tarefa,
    handle_listar_tarefas,
)
from assistant.storage import TaskRepository, format_time_for_speech


@pytest.fixture()
def repository(tmp_path: Path) -> TaskRepository:
    data_path = tmp_path / "data"
    return TaskRepository(data_path)


def test_add_and_list_tasks(repository: TaskRepository) -> None:
    result = handle_listar_tarefas(repository)
    assert "não tem tarefas" in result.message

    add_result = handle_adicionar_tarefa(repository, "Lavar a louça")
    assert "Adicionei a tarefa" in add_result.message

    list_result = handle_listar_tarefas(repository)
    assert "Tarefas pendentes" in list_result.message
    assert "Lavar a louça" in list_result.message


def test_complete_task(repository: TaskRepository) -> None:
    task_result = handle_adicionar_tarefa(repository, "Enviar relatório")
    task_id = int(task_result.message.split("#")[1].split(" ")[0])

    completion = handle_concluir_tarefa(repository, task_id)
    assert "está concluída" in completion.message

    list_result = handle_listar_tarefas(repository)
    assert "Concluídas" in list_result.message


def test_add_with_reminder_confirmation(repository: TaskRepository) -> None:
    reminder_time = time(hour=14)
    add_result = handle_adicionar_tarefa(
        repository,
        "Reunião com o time",
        reminder_time=reminder_time,
        require_confirmation=True,
    )

    assert add_result.confirmation is not None
    assert format_time_for_speech(reminder_time) in add_result.message

    confirmation = add_result.confirmation
    confirm_result = handle_confirmar_lembrete(
        repository,
        confirmation.id,
        accepted=True,
    )
    assert "Vou lembrar" in confirm_result.message

    list_result = handle_listar_tarefas(repository)
    assert "lembrete" in list_result.message
    assert format_time_for_speech(reminder_time) in list_result.message


def test_decline_reminder_confirmation(repository: TaskRepository) -> None:
    reminder_time = time(hour=16, minute=30)
    add_result = handle_adicionar_tarefa(
        repository,
        "Comprar presentes",
        reminder_time=reminder_time,
        require_confirmation=True,
    )

    confirmation = add_result.confirmation
    assert confirmation is not None

    decline_result = handle_confirmar_lembrete(
        repository,
        confirmation.id,
        accepted=False,
    )
    assert "não vou adicionar o lembrete" in decline_result.message

    list_result = handle_listar_tarefas(repository)
    assert format_time_for_speech(reminder_time) not in list_result.message

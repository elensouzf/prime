"""Domain intents supported by the assistant."""
from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    """Known intents for interacting with the task assistant."""

    LISTAR_TAREFAS = "listar_tarefas"
    ADICIONAR_TAREFA = "adicionar_tarefa"
    CONCLUIR_TAREFA = "concluir_tarefa"
    CONFIRMAR_LEMBRETE = "confirmar_lembrete"


__all__ = ["Intent"]

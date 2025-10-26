# Assistente de tarefas

Este projeto implementa um conjunto de intents para gerenciar tarefas em português, com suporte a confirmações de lembrete e respostas humanizadas.

## Intents disponíveis
- `listar_tarefas`: retorna um resumo amigável das tarefas pendentes e concluídas.
- `adicionar_tarefa`: cria uma nova tarefa e, opcionalmente, solicita confirmação para adicionar um lembrete.
- `concluir_tarefa`: marca uma tarefa como concluída.
- `confirmar_lembrete`: aplica ou descarta um lembrete previamente solicitado.

## Entidade `Task`
Cada tarefa possui:
- `id`: identificador incremental.
- `description`: descrição textual.
- `status`: `pending` ou `completed`.
- `created_at` e `updated_at`: timestamps em UTC.
- `reminder_time`: horário opcional armazenado no formato `HH:MM`.

## Executando os testes

Instale as dependências opcionais de desenvolvimento e execute o Pytest:

```bash
pip install -e .[dev]
pytest
```

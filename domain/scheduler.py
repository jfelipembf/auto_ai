from __future__ import annotations

import asyncio
from typing import Dict

from settings import CONFIG
from db.base import get_session, engine
from db.fila import FilaRepositoryImpl
from db.historico import HistoricoRepositoryImpl
from services.evolution_api import send_text


REPLY_TEXT = "A evolution está ativa?"


class DebounceScheduler:
    _instance: "DebounceScheduler" | None = None

    def __init__(self) -> None:
        self._tasks: Dict[str, asyncio.Task] = {}
        self._debounce_seconds: int = int(CONFIG.get("DEBOUNCE_SECONDS", 6))

    @classmethod
    def instance(cls) -> "DebounceScheduler":
        if cls._instance is None:
            cls._instance = DebounceScheduler()
        return cls._instance

    def schedule(self, phone_number: str) -> None:
        # Cancela tarefa anterior (reinicia o timer)
        t = self._tasks.get(phone_number)
        if t and not t.done():
            t.cancel()
        self._tasks[phone_number] = asyncio.create_task(self._run(phone_number))

    async def _run(self, phone_number: str) -> None:
        try:
            await asyncio.sleep(self._debounce_seconds)
        except asyncio.CancelledError:
            return

        # Lê fila do banco, concatena, envia, limpa e registra histórico do agente
        if engine is None:
            # Sem banco: apenas envia a mensagem padrão
            await send_text(phone_number, REPLY_TEXT)
            return

        try:
            with get_session() as db:
                fila_repo = FilaRepositoryImpl(db)
                historico_repo = HistoricoRepositoryImpl(db)

                itens = fila_repo.list_by_phone(phone_number)
                # Concatena mensagens por ordem
                texto = "\n".join(x.mensagem for x in itens if (x.mensagem or "").strip())

                # Envia resposta (podemos incluir o texto concatenado no futuro)
                await send_text(phone_number, REPLY_TEXT)

                # Limpa fila
                fila_repo.clear_by_phone(phone_number)

                # Registra resposta do agente
                historico_repo.append(session_id=phone_number, msg_type="ai", content=REPLY_TEXT)
        except Exception:
            # Não propaga exceção para não derrubar o loop
            pass

from __future__ import annotations

from typing import Dict, Any

from domain.models import MessageIn, MessageOut
from settings import CONFIG
from services.evolution_api import send_text, send_presence, mark_as_read

from db.base import get_session, engine
from db.fila import FilaRepositoryImpl
from db.historico import HistoricoRepositoryImpl
from domain.scheduler import DebounceScheduler


REPLY_TEXT = "A evolution está ativa?"


class ProcessIncomingMessageUseCase:
    async def handle(self, message: MessageIn) -> MessageOut:
        if not message.phone_number:
            return MessageOut(ok=False, echo=None, details={"reason": "number_not_found"})

        # 1) Opcional: persistir em fila/histórico se banco estiver disponível
        if engine is not None:
            try:
                with get_session() as db:
                    FilaRepositoryImpl(db).add(
                        telefone=message.phone_number,
                        mensagem=message.text or "",
                        id_mensagem=message.message_id,
                    )
                    # registra o user (entrada)
                    if message.text:
                        HistoricoRepositoryImpl(db).append(
                            session_id=message.phone_number, msg_type="user", content=message.text
                        )
            except Exception:
                # Não interromper o fluxo caso o banco falhe
                pass

        # 2) Opcional: marcar como lida
        try:
            if message.message_id and (message.remote_jid or message.phone_number):
                remote = message.remote_jid or message.phone_number
                await mark_as_read(message.message_id, remote, bool(message.from_me))
        except Exception:
            pass

        # 3) Enviar presença curta e agendar processamento por telefone (debounce)
        try:
            await send_presence(message.phone_number, presence="composing", delay_ms=600)
        except Exception:
            pass

        # Processamento imediato (útil em ambientes que reciclam o processo e cancelam tasks)
        if CONFIG.get("SYNC_PROCESSING"):
            await DebounceScheduler.instance().run_now(message.phone_number)
        else:
            # Agenda processamento assíncrono por telefone; resposta será enviada pelo scheduler
            DebounceScheduler.instance().schedule(message.phone_number)

        return MessageOut(ok=True, echo=REPLY_TEXT, details={"scheduled": True})

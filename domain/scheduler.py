from __future__ import annotations

import asyncio
from typing import Dict

from settings import CONFIG
from db.base import get_session, engine
from db.fila import FilaRepositoryImpl
from db.historico import HistoricoRepositoryImpl
from domain.usecases.respond_with_ai import RespondWithAIUseCase
from services.evolution_api import get_audio_base64
from services.openai_api import transcribe_audio
import base64


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

        # Lê fila do banco, concatena, gera resposta com IA, limpa fila
        if engine is None:
            # Sem banco: gera e envia resposta só com concat (sem histórico persistido)
            # Para simplicidade, se não houver DB, respondemos com texto fixo
            # (você pode adaptar para chamar IA sem histórico)
            from services.evolution_api import send_text
            await send_text(phone_number, REPLY_TEXT)
            return

        try:
            with get_session() as db:
                fila_repo = FilaRepositoryImpl(db)
                historico_repo = HistoricoRepositoryImpl(db)

                itens = fila_repo.list_by_phone(phone_number)
                partes: list[str] = []
                for x in itens:
                    msg_txt = (x.mensagem or "").strip()
                    if msg_txt:
                        partes.append(msg_txt)
                        continue

                    # Se não há texto, mas há id_mensagem, tentamos baixar/transcrever áudio
                    if x.id_mensagem:
                        try:
                            media = await get_audio_base64(x.id_mensagem)
                            if media.get("ok") and media.get("data"):
                                b64 = media["data"].split(",")[-1]
                                audio_bytes = base64.b64decode(b64)
                                texto_audio = await transcribe_audio(audio_bytes, filename="audio.ogg")
                                if texto_audio.strip():
                                    partes.append(texto_audio.strip())
                                    # Persistir no histórico como user (transcrição)
                                    historico_repo.append(session_id=phone_number, msg_type="user", content=texto_audio.strip())
                        except Exception:
                            # ignora erros de transcrição/baixa para não travar o fluxo
                            pass

                texto = "\n".join(p for p in partes if p)

                # Gera e envia resposta com IA
                try:
                    await RespondWithAIUseCase().handle(phone_number, texto)
                except Exception:
                    # fallback em caso de erro da IA
                    from services.evolution_api import send_text
                    await send_text(phone_number, REPLY_TEXT)

                # Limpa fila após responder
                fila_repo.clear_by_phone(phone_number)
        except Exception:
            # Em qualquer erro (DB/IA/etc), responde com fallback para não ficar mudo
            try:
                from services.evolution_api import send_text
                await send_text(phone_number, REPLY_TEXT)
            except Exception:
                pass

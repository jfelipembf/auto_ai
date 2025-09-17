from __future__ import annotations

from typing import List, Dict

from utils.prompt_loader import load_prompt
from services.openai_api import chat
from services.evolution_api import send_text
from db.base import get_session
from db.historico import HistoricoRepositoryImpl


SYSTEM_PROMPT_NAME = "cibelly_pt"


class RespondWithAIUseCase:
    async def handle(self, phone_number: str, latest_user_concat: str) -> str:
        """Monta contexto com histórico + prompt da Cibelly e gera resposta com OpenAI.
        Envia a resposta ao usuário via Evolution e persiste no histórico.
        Retorna o texto enviado.
        """
        system = load_prompt(SYSTEM_PROMPT_NAME) or "Você é Cibelly."

        # Monta mensagens com histórico recente
        with get_session() as db:
            historico_repo = HistoricoRepositoryImpl(db)
            history = historico_repo.list_by_session(phone_number, limit=50)

        messages: List[Dict[str, str]] = []
        for item in history:
            msg = item.message or {}
            t = msg.get("type")
            c = (msg.get("content") or "").strip()
            if not c:
                continue
            if t == "user":
                messages.append({"role": "user", "content": c})
            elif t == "ai":
                messages.append({"role": "assistant", "content": c})

        # Adiciona o batch mais recente (concat) como última mensagem do usuário
        if latest_user_concat.strip():
            messages.append({"role": "user", "content": latest_user_concat.strip()})

        # Chama OpenAI
        reply_text = await chat(system_prompt=system, messages=messages)

        # Envia e persiste
        await send_text(phone_number, reply_text)
        with get_session() as db2:
            HistoricoRepositoryImpl(db2).append(session_id=phone_number, msg_type="ai", content=reply_text)

        return reply_text

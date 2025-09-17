# Modelo ou função para:
# - Armazenar histórico do chat (por agente e por sessão)
# - Usado pela memória e auditoria

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, Session

from db.base import Base


class HistoricoMensagem(Base):
    __tablename__ = "n8n_historico_mensagens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class HistoricoRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def append(self, session_id: str, msg_type: Literal["user", "ai"], content: str):
        item = HistoricoMensagem(session_id=session_id, message={"type": msg_type, "content": content})
        self.session.add(item)
        self.session.flush()
        return item

    def list_by_session(self, session_id: str, limit: int = 20):
        q = (
            self.session.query(HistoricoMensagem)
            .filter(HistoricoMensagem.session_id == session_id)
            .order_by(HistoricoMensagem.created_at.asc())
        )
        if limit:
            q = q.limit(limit)
        return q.all()

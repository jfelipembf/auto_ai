from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session

from db.base import Base


class FilaMensagem(Base):
    __tablename__ = "n8n_fila_mensagens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telefone: Mapped[str] = mapped_column(String(32), index=True)
    mensagem: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    id_mensagem: Mapped[str] = mapped_column(String(128), nullable=True)


class FilaRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def add(self, telefone: str, mensagem: str, id_mensagem: str | None = None, ts: datetime | None = None) -> FilaMensagem:
        item = FilaMensagem(
            telefone=telefone,
            mensagem=mensagem,
            id_mensagem=id_mensagem,
            timestamp=ts or datetime.utcnow(),
        )
        self.session.add(item)
        self.session.flush()
        return item

    def list_by_phone(self, telefone: str) -> List[FilaMensagem]:
        return (
            self.session.query(FilaMensagem)
            .filter(FilaMensagem.telefone == telefone)
            .order_by(FilaMensagem.timestamp.asc())
            .all()
        )

    def clear_by_phone(self, telefone: str) -> int:
        q = self.session.query(FilaMensagem).filter(FilaMensagem.telefone == telefone)
        count = q.count()
        q.delete(synchronize_session=False)
        return count

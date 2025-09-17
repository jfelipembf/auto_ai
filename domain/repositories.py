from __future__ import annotations

from typing import Protocol, List, Optional
from datetime import datetime


class FilaRepository(Protocol):
    def add(self, telefone: str, mensagem: str, id_mensagem: Optional[str] = None, ts: Optional[datetime] = None):
        ...

    def list_by_phone(self, telefone: str) -> List:
        ...

    def clear_by_phone(self, telefone: str) -> int:
        ...


class HistoricoRepository(Protocol):
    def append(self, session_id: str, msg_type: str, content: str):
        ...

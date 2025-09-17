from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel


class MessageIn(BaseModel):
    phone_number: str
    message_id: Optional[str] = None
    remote_jid: Optional[str] = None
    from_me: Optional[bool] = None
    text: Optional[str] = None
    is_audio: Optional[bool] = None
    timestamp: Optional[int] = None
    raw: Dict[str, Any] = {}


class MessageOut(BaseModel):
    ok: bool
    echo: Optional[str] = None
    details: Dict[str, Any] = {}

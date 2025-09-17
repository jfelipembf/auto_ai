from __future__ import annotations

from typing import Any, Dict, Optional
from domain.models import MessageIn


def normalize_number(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = str(raw)
    if "@" in s:
        s = s.split("@", 1)[0]
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits or None


def extract_message_in(payload: Dict[str, Any]) -> Optional[MessageIn]:
    if not isinstance(payload, dict):
        return None

    # direct fields
    number = None
    text = None
    message_id = None
    remote_jid = None
    from_me = None
    timestamp = None
    is_audio = None

    # common shapes
    if isinstance(payload.get("message"), dict):
        number = payload["message"].get("from") or number
        text = payload["message"].get("body") or text
    for k in ("from", "number", "remoteJid"):
        number = number or payload.get(k)

    if payload.get("sender") and isinstance(payload["sender"], dict):
        for k in ("id", "phone", "waId"):
            number = number or payload["sender"].get(k)

    for k in ("chatId", "waId"):
        number = number or payload.get(k)

    # nested 'data'
    data = payload.get("data")
    if isinstance(data, dict):
        key = data.get("key")
        if isinstance(key, dict):
            remote_jid = key.get("remoteJid") or remote_jid
            from_me = key.get("fromMe") if from_me is None else from_me
            message_id = key.get("id") or message_id
        # messages list variant
        msgs = data.get("messages") or data.get("message")
        if isinstance(msgs, list) and msgs:
            first = msgs[0]
            if isinstance(first, dict):
                k = first.get("key")
                if isinstance(k, dict):
                    remote_jid = k.get("remoteJid") or remote_jid
                    from_me = k.get("fromMe") if from_me is None else from_me
                    message_id = k.get("id") or message_id
                for kk in ("from", "number", "remoteJid"):
                    number = number or first.get(kk)
                # text candidates
                text = (
                    first.get("message", {}).get("conversation")
                    or first.get("conversation")
                    or text
                )
        # detect audio in nested message
        msg = data.get("message")
        if isinstance(msg, dict):
            audio_msg = msg.get("audioMessage")
            if isinstance(audio_msg, dict):
                # ptt true indica áudio de voz
                is_audio = bool(audio_msg.get("ptt", True)) or True

        # more text candidates
        text = (
            text
            or data.get("message", {}).get("conversation")
            or data.get("conversation")
            or payload.get("message")
            or payload.get("text")
        )
        timestamp = data.get("messageTimestamp") or timestamp

    # top-level messages (array)
    msgs2 = payload.get("messages") or payload.get("message")
    if isinstance(msgs2, list) and msgs2:
        first = msgs2[0]
        if isinstance(first, dict):
            k = first.get("key")
            if isinstance(k, dict):
                remote_jid = k.get("remoteJid") or remote_jid
                from_me = k.get("fromMe") if from_me is None else from_me
                message_id = k.get("id") or message_id
            for kk in ("from", "number", "remoteJid"):
                number = number or first.get(kk)
            # audio detection on top-level
            msg = first.get("message") or {}
            if isinstance(msg, dict):
                audio_msg = msg.get("audioMessage")
                if isinstance(audio_msg, dict):
                    is_audio = bool(audio_msg.get("ptt", True)) or True
            text = msg.get("conversation") or first.get("conversation") or text

    phone = normalize_number(number)
    return MessageIn(
        phone_number=phone or "",
        message_id=message_id,
        remote_jid=remote_jid,
        from_me=from_me,
        text=(text or "").strip() or None,
        is_audio=is_audio,
        timestamp=timestamp if isinstance(timestamp, int) else None,
        raw=payload,
    )

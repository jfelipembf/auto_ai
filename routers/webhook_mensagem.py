from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.evolution_api import send_text, send_presence
from utils.logger import get_logger

router = APIRouter()
log = get_logger("webhook_mensagem")


def _normalize_number(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw)
    # casos de JID: 5511999999999@s.whatsapp.net
    if "@" in s:
        s = s.split("@", 1)[0]
    # apenas dígitos
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits or None


def _extract_number(payload: dict) -> str | None:
    """Tenta extrair número do remetente de formatos comuns de webhook Evolution.

    Exemplos esperados:
    - {"message": {"from": "5511999999999", "body": "..."}}
    - {"from": "5511999999999", "message": "..."}
    - {"number": "5511999999999", ...}
    """
    if not isinstance(payload, dict):
        return None
    # formatos diretos
    if isinstance(payload.get("message"), dict):
        frm = payload["message"].get("from")
        if frm:
            return _normalize_number(frm)
    for key in ("from", "number", "remoteJid"):
        val = payload.get(key)
        if val:
            return _normalize_number(val)

    # formatos aninhados comuns na Evolution
    # 1) payload.get("data", {}).get("key", {}).get("remoteJid")
    data = payload.get("data")
    if isinstance(data, dict):
        key = data.get("key")
        if isinstance(key, dict):
            rj = key.get("remoteJid")
            if rj:
                return _normalize_number(rj)

        # 2) data.get("messages") -> lista com elementos contendo key.remoteJid
        msgs = data.get("messages") or data.get("message")
        if isinstance(msgs, list) and msgs:
            first = msgs[0]
            if isinstance(first, dict):
                k = first.get("key")
                if isinstance(k, dict) and k.get("remoteJid"):
                    return _normalize_number(k["remoteJid"])
                # fallback: campos comuns
                for key in ("from", "number", "remoteJid"):
                    if first.get(key):
                        return _normalize_number(first[key])
    return None


@router.post("/anota")
async def webhook_anota(request: Request):
    """Webhook de mensagens.

    Ao receber uma nova mensagem, responde automaticamente com:
    "A evolution está ativa?"
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    log.info(f"/anota payload: {data}")

    number = _extract_number(data)
    if not number:
        log.warning("numero nao encontrado no payload")
        return JSONResponse(status_code=200, content={"ok": False, "reason": "number_not_found"})

    # Opcional: enviar presença de 'digitando' breve
    await send_presence(number, presence="composing", delay_ms=600)

    # Responder com a mensagem desejada
    texto = "A evolution está ativa?"
    try:
        resp = await send_text(number, texto)
        log.info(f"mensagem enviada para {number}: {resp}")
        return {"ok": True, "echo": texto, "evolution": resp}
    except Exception as e:
        log.error(f"erro ao enviar mensagem para {number}: {e}")
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


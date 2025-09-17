from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.evolution_api import send_text, send_presence

router = APIRouter()


def _extract_number(payload: dict) -> str | None:
    """Tenta extrair número do remetente de formatos comuns de webhook Evolution.

    Exemplos esperados:
    - {"message": {"from": "5511999999999", "body": "..."}}
    - {"from": "5511999999999", "message": "..."}
    - {"number": "5511999999999", ...}
    """
    if not isinstance(payload, dict):
        return None
    # formatos:
    if isinstance(payload.get("message"), dict):
        frm = payload["message"].get("from")
        if frm:
            return str(frm)
    for key in ("from", "number", "remoteJid"):
        val = payload.get(key)
        if val:
            return str(val)
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

    number = _extract_number(data)
    if not number:
        return JSONResponse(status_code=200, content={"ok": False, "reason": "number_not_found"})

    # Opcional: enviar presença de 'digitando' breve
    await send_presence(number, presence="composing", delay_ms=600)

    # Responder com a mensagem desejada
    texto = "A evolution está ativa?"
    resp = await send_text(number, texto)

    return {"ok": True, "echo": texto, "evolution": resp}


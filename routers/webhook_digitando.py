from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.evolution_api import send_presence

router = APIRouter()


@router.post("/consulta")
async def webhook_consulta(request: Request):
    """Recebe payload e envia presença (digitando/gravando).

    Payload aceito (qualquer dos campos):
    - number: "5511999999999"
    - presence: "composing" | "recording" | "paused" (default: composing)
    - delay: inteiro em ms (default: 800)
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    number = data.get("number") or data.get("from")
    presence = data.get("presence", "composing")
    delay = int(data.get("delay", 800))

    if not number:
        return JSONResponse(status_code=200, content={"ok": False, "reason": "number_not_found"})

    resp = await send_presence(str(number), str(presence), delay)
    return {"ok": True, "presence": presence, "delay": delay, "evolution": resp}


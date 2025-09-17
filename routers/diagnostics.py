from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.evolution_api import send_text
from utils.logger import get_logger
from settings import CONFIG

router = APIRouter()
log = get_logger("diagnostics")


@router.get("/health")
async def health():
    return {
        "ok": True,
        "service": "auto_ai",
        "evolution": {
            "url_configured": bool(CONFIG.get("EVOLUTION_API_URL")),
            "instance_configured": bool(CONFIG.get("EVOLUTION_INSTANCE")),
            "api_key_configured": bool(CONFIG.get("EVOLUTION_API_KEY")),
        },
    }


@router.post("/send")
async def send_message(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    number = (data.get("number") or data.get("to") or "").strip()
    text = (data.get("text") or data.get("message") or "teste").strip()

    if not number:
        return JSONResponse(status_code=400, content={"ok": False, "error": "missing number"})

    try:
        resp = await send_text(number, text)
        log.info(f"diagnostics /send -> {number} : {resp}")
        return {"ok": True, "evolution": resp}
    except Exception as e:
        log.error(f"diagnostics /send error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

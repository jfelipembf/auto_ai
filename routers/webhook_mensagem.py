from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from domain.helpers import extract_message_in
from domain.usecases.process_incoming_message import ProcessIncomingMessageUseCase

router = APIRouter()


@router.post("/anota")
async def webhook_anota(request: Request):
    """Webhook de mensagens: delega para o caso de uso de domínio.

    Ao receber uma nova mensagem, responde automaticamente com "A evolution está ativa?".
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    message_in = extract_message_in(data) or None
    if not message_in or not message_in.phone_number:
        return JSONResponse(status_code=200, content={"ok": False, "reason": "number_not_found"})

    usecase = ProcessIncomingMessageUseCase()
    try:
        out = await usecase.handle(message_in)
        return out.model_dump()
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})



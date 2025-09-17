"""
Client wrapper para Evolution API.

Funções principais expostas:
- send_text(number: str, text: str) -> envia mensagem de texto

Observações:
- Usa variáveis de ambiente definidas em `settings.py` (EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE)
- Implementado com httpx (assíncrono) para compatibilidade com FastAPI
"""

from typing import Any, Dict, Optional

import httpx

from settings import CONFIG


BASE_URL: str = (CONFIG.get("EVOLUTION_API_URL") or "").rstrip("/")
API_KEY: Optional[str] = CONFIG.get("EVOLUTION_API_KEY")
INSTANCE: Optional[str] = CONFIG.get("EVOLUTION_INSTANCE")


def _headers() -> Dict[str, str]:
    """Gera headers de autenticação aceitando formatos comuns da Evolution API.

    Conforme a documentação oficial, o header suportado é 'apikey'.
    Algumas instalações também aceitam/esperam 'Authorization: Bearer <key>'.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if API_KEY:
        headers["apikey"] = API_KEY
        headers["X-API-Key"] = API_KEY  # algumas instalações utilizam este cabeçalho
        # Compatibilidade com instalações que validam via Bearer
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def _instance_path(path: str) -> str:
    if not BASE_URL or not INSTANCE:
        raise RuntimeError(
            "EVOLUTION_API_URL e/ou EVOLUTION_INSTANCE não configurados. Verifique o arquivo .env"
        )
    # Normalmente: /message/sendText/{instanceId}
    return f"{BASE_URL.rstrip('/')}/{path.strip('/').rstrip('/')}/{INSTANCE}"


async def send_text(number: str, text: str) -> Dict[str, Any]:
    """Envia mensagem de texto para um número (apenas dígitos, com DDI), ex: 5511999999999.

    Retorna o JSON de resposta da Evolution API.
    """
    url = _instance_path("message/sendText")
    payload = {"number": number, "text": text}

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.json()


async def send_presence(number: str, presence: str = "composing", delay_ms: int = 800) -> Dict[str, Any]:
    """Opcional: envia presença (digitando/gravação). Ignora silenciosamente se endpoint não existir.

    presence comuns: 'composing' (digitando), 'recording' (gravando), 'paused'
    """
    try:
        url = _instance_path("message/sendPresence")
        payload = {"number": number, "presence": presence, "delay": delay_ms}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=_headers(), json=payload)
            if resp.is_success:
                return resp.json()
            return {"ok": False, "status_code": resp.status_code, "text": resp.text}
    except Exception as e:
        # Não falha o fluxo principal por presença
        return {"ok": False, "error": str(e)}


def _ensure_remote_jid(remote: str) -> str:
    s = str(remote)
    return s if "@" in s else f"{s}@s.whatsapp.net"


async def mark_as_read(message_id: str, remote_jid: str, from_me: bool = False) -> Dict[str, Any]:
    """Marca uma ou mais mensagens como lidas.

    Evolution espera payload no formato:
    {"readMessages": [{"id": "...", "remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false}]}
    """
    url = _instance_path("chat/markMessageAsRead")
    payload = {
        "readMessages": [
            {
                "id": message_id,
                "remoteJid": _ensure_remote_jid(remote_jid),
                "fromMe": bool(from_me),
            }
        ]
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.json()

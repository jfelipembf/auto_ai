from __future__ import annotations

import io
from typing import List, Dict, Any, Optional

import httpx

from settings import CONFIG


OPENAI_API_KEY = CONFIG.get("OPENAI_API_KEY")
CHAT_MODEL = CONFIG.get("OPENAI_MODEL") or "gpt-4o-mini"
TRANSCRIBE_MODEL = CONFIG.get("OPENAI_TRANSCRIBE_MODEL", "whisper-1")


def _headers() -> Dict[str, str]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurado")
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }


async def chat(system_prompt: str, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    """Faz uma chamada ao Chat Completions e retorna o conteúdo de texto.

    messages: lista de {role: 'system'|'user'|'assistant', content: '...'}
    """
    use_model = model or CHAT_MODEL
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": use_model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.4,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers={**_headers(), "Content-Type": "application/json"}, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def transcribe_audio(file_bytes: bytes, filename: str = "audio.wav", model: Optional[str] = None) -> str:
    """Transcreve áudio com Whisper API (ou modelo definido) e retorna texto."""
    use_model = model or TRANSCRIBE_MODEL
    url = "https://api.openai.com/v1/audio/transcriptions"

    # Multipart form data
    files = {
        "file": (filename, io.BytesIO(file_bytes), "audio/wav"),
        "model": (None, use_model),
        "response_format": (None, "text"),
        "temperature": (None, "0"),
        # "language": (None, "pt"),  # habilite se desejar fixar idioma
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, headers=_headers(), files=files)
        resp.raise_for_status()
        return resp.text.strip()

#!/usr/bin/env python3
"""
Script de teste para enviar mensagem via Evolution API diretamente,
seguindo a documentação oficial.

Uso:
  python scripts/test_send_text.py 55DDDNÚMERO "Mensagem aqui"

Requisitos:
  - Variáveis no .env: EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE
  - Pacotes: requests
"""
import sys
import os
import json
import requests

# Garante que o diretório raiz do projeto esteja no sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from settings import CONFIG


def main():
    if len(sys.argv) < 3:
        print("Uso: python scripts/test_send_text.py 55DDDNÚMERO \"Mensagem aqui\"")
        sys.exit(1)

    number = sys.argv[1]
    text = sys.argv[2]

    base_url = (CONFIG.get("EVOLUTION_API_URL") or "").rstrip("/")
    instance = CONFIG.get("EVOLUTION_INSTANCE")
    apikey = CONFIG.get("EVOLUTION_API_KEY")

    if not base_url or not instance or not apikey:
        print("ERRO: Configure EVOLUTION_API_URL, EVOLUTION_INSTANCE e EVOLUTION_API_KEY no .env")
        sys.exit(2)

    def do_request(current_base: str):
        url = f"{current_base}/message/sendText/{instance}"
        headers = {
            "Content-Type": "application/json",
            "apikey": apikey,
            # compatibilidade com algumas instalações
            "Authorization": f"Bearer {apikey}",
        }
        payload = {"number": number, "text": text}
        print(f"POST {url}\nPayload: {json.dumps(payload)}")
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"Status: {resp.status_code}")
        try:
            print("Resposta:", resp.json())
        except Exception:
            print("Resposta (texto):", resp.text)
        return resp

    # tentativa 1: base do .env
    resp = do_request(base_url)
    # fallback: tentar base com /api
    if resp.status_code in (401, 403, 404) and not base_url.endswith("/api"):
        alt_base = base_url + "/api"
        print("\nTentando novamente com base_url /api...")
        resp = do_request(alt_base)


if __name__ == "__main__":
    main()

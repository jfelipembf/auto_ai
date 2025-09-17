#!/usr/bin/env python3
"""
Pequeno tester para o webhook /anota.

Uso:
  python3 scripts/test_webhook.py --url https://seu-dominio/ [--mode simple|body] [--number 5579999371622]

Se não passar argumentos, tenta usar variáveis de ambiente:
  APP_URL, TEST_NUMBER

Exemplos:
  python3 scripts/test_webhook.py --url https://contrato-intelitec-auto2.re1ifw.easypanel.host --mode simple --number 5579999371622
  python3 scripts/test_webhook.py --url https://contrato-intelitec-auto2.re1ifw.easypanel.host --mode body   --number 5579999371622
"""
import json
import os
import sys
import argparse
import urllib.request


def http_get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode("utf-8", errors="ignore")


def http_post(url: str, payload: dict) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        # tentar extrair corpo de erro
        if hasattr(e, 'read'):
            try:
                body = e.read().decode('utf-8', errors='ignore')
            except Exception:
                body = str(e)
            return getattr(e, 'code', 0) or 0, body
        return 0, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("APP_URL", ""))
    parser.add_argument("--mode", choices=["simple", "body"], default="simple")
    parser.add_argument("--number", default=os.getenv("TEST_NUMBER", "5579999371622"))
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    if not base_url:
        print("Erro: informe --url ou defina APP_URL no ambiente.")
        sys.exit(2)

    # 1) Health
    status, body = http_get(f"{base_url}/health")
    print("[GET /health]", status, body)

    # 2) POST /anota
    if args.mode == "simple":
        payload = {"from": args.number, "message": "oi, quero agendar"}
    else:
        payload = {
            "body": {
                "server_url": os.getenv("EVOLUTION_API_URL", "https://evolution-evolution-api.re1ifw.easypanel.host"),
                "instance": os.getenv("EVOLUTION_INSTANCE", "anota"),
                "data": {
                    "key": {
                        "id": "MSG_ID_EXEMPLO",
                        "remoteJid": f"{args.number}@s.whatsapp.net",
                        "fromMe": False
                    },
                    "message": {"conversation": "oi, quero agendar"},
                    "messageTimestamp": 1726500000
                }
            }
        }

    status, body = http_post(f"{base_url}/anota", payload)
    print("[POST /anota]", status, body)


if __name__ == "__main__":
    main()

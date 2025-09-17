from fastapi import FastAPI
from routers import webhook_mensagem, webhook_digitando

app = FastAPI()

app.include_router(webhook_mensagem.router)
app.include_router(webhook_digitando.router)


@app.get("/")
def index():
    return {"ok": True, "service": "auto_ai", "version": 1}


@app.get("/health")
def health():
    return {"ok": True}

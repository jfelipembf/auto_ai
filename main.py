from fastapi import FastAPI
from routers import webhook_mensagem, webhook_digitando

app = FastAPI()

app.include_router(webhook_mensagem.router)
app.include_router(webhook_digitando.router)

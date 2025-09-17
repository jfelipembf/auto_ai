from fastapi import FastAPI
from routers import webhook_mensagem, webhook_digitando
from routers import diagnostics

app = FastAPI()

app.include_router(webhook_mensagem.router)
app.include_router(webhook_digitando.router)
app.include_router(diagnostics.router)

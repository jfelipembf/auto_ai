from fastapi import FastAPI
from routers import webhook_mensagem, webhook_digitando
import logging
from db.base import init_db, list_tables

app = FastAPI()

app.include_router(webhook_mensagem.router)
app.include_router(webhook_digitando.router)


@app.get("/")
def index():
    return {"ok": True, "service": "auto_ai", "version": 1}


@app.get("/health")
def health():
    return {"ok": True}


@app.on_event("startup")
def on_startup():
    logging.basicConfig(level=logging.INFO)
    try:
        res = init_db()
        logging.info({"init_db": res})
        tables = list_tables()
        logging.info({"tables": tables})
    except Exception as e:
        logging.warning({"init_db_error": str(e)})

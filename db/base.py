from __future__ import annotations

import contextlib
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from settings import CONFIG


POSTGRES_URL = CONFIG.get("POSTGRES_URL")


class Base(DeclarativeBase):
    pass


engine = create_engine(POSTGRES_URL) if POSTGRES_URL else None
SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
)


@contextlib.contextmanager
def get_session():
    if not SessionLocal:
        raise RuntimeError("POSTGRES_URL não configurado")
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> dict:
    """Cria as tabelas necessárias se não existirem.

    Importa os modelos para registrá-los no metadata e executa create_all.
    Retorna um resumo com as tabelas detectadas após a criação.
    """
    if engine is None:
        return {"ok": False, "reason": "no_engine"}

    # Importa modelos para registrar no metadata
    from db import fila as _fila  # noqa: F401
    from db import historico as _historico  # noqa: F401

    Base.metadata.create_all(engine)
    insp = inspect(engine)
    tables = insp.get_table_names()
    return {"ok": True, "tables": tables}


def list_tables() -> dict:
    if engine is None:
        return {"ok": False, "reason": "no_engine"}
    insp = inspect(engine)
    return {"ok": True, "tables": insp.get_table_names()}

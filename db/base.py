from __future__ import annotations

import contextlib
from sqlalchemy import create_engine
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

from __future__ import annotations
import os
from urllib.parse import urlparse

import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from dotenv import load_dotenv
load_dotenv()


def _get_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    raise RuntimeError(
        "Configure a URL do banco em .streamlit/secrets.toml (postgres.url) "
        "ou na variável de ambiente DATABASE_URL."
    )


class Database:
    def __init__(self, url: str):
        self._engine: Engine = create_engine(url, pool_pre_ping=True)
        with self._engine.connect() as c:
            c.execute(text("SELECT 1"))

    @property
    def engine(self) -> Engine:
        return self._engine

    # ✅ agora aceita params
    def fetch_all(self, sql: str, params: dict | None = None) -> list[dict]:
        with self._engine.connect() as c:
            res = c.execute(text(sql), params or {})
            return [dict(r) for r in res.mappings().all()]  # rows como dict

    # ✅ agora aceita params
    def fetch_one(self, sql: str, params: dict | None = None) -> dict | None:
        with self._engine.connect() as c:
            res = c.execute(text(sql), params or {})
            row = res.mappings().first()
            return dict(row) if row else None

    def fetch_one_tx(self, sql: str, params: dict | None = None) -> dict | None:
        with self._engine.begin() as c:          # <-- transação COMMIT automática
            res = c.execute(text(sql), params or {})
            row = res.mappings().first()
            return dict(row) if row else None

    def execute(self, sql: str, params: dict | None = None) -> None:
        with self._engine.begin() as c:  # transação p/ writes
            c.execute(text(sql), params or {})

@st.cache_resource(show_spinner=False)
def get_db() -> Database:
    """Singleton (por processo) para o Database no Streamlit."""
    url = _get_db_url()
    return Database(url)

from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.database_url = None
        if "postgres" in st.secrets:
            self.database_url = st.secrets["postgres"].get("url")
        if not self.database_url:
            self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError(
                "Define the URL for DATABASE in .streamlit/secrets.toml or .env DATABASE_URL"
            )

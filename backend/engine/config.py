"""
config.py — Centralized configuration loaded from .env

All other modules import `from config import config` to read settings.
This keeps environment variable access in one place and makes testing easier.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve .env relative to this file (engine root)
_ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=False)


class Config:
    # ── LLM ──────────────────────────────────────────────────────────────────
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

    # ── Databases ─────────────────────────────────────────────────────────────
    # Paths are relative to the engine root (where this file lives)
    _ENGINE_ROOT = Path(__file__).parent
    DATASET_DB_PATH: str = str(
        _ENGINE_ROOT / os.getenv("DATASET_DB_PATH", "data/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db")
    )
    OPERATIONAL_DB_PATH: str = str(
        _ENGINE_ROOT / os.getenv("OPERATIONAL_DB_PATH", "data/agent-data/agent.db")
    )

    # ── Agent limits ──────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
    MAX_TOOL_CALLS: int = int(os.getenv("MAX_TOOL_CALLS", "20"))
    MAX_GRAPH_DEPTH: int = int(os.getenv("MAX_GRAPH_DEPTH", "15"))
    MAX_ACCOUNTS_INVESTIGATED: int = int(os.getenv("MAX_ACCOUNTS_INVESTIGATED", "10"))
    MAX_EXECUTION_TIME: int = int(os.getenv("MAX_EXECUTION_TIME", "300"))


config = Config()

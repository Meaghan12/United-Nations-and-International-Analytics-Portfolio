"""
utils/config.py
===============
Centralised configuration loader.

Priority order:
1. Streamlit secrets (st.secrets) — used on Streamlit Community Cloud
2. Environment variable — used locally with .env
3. Demo mode — used when no key is available at all

NEVER log, print, or expose the key value.
"""
from __future__ import annotations
import os


def get_openai_key() -> str | None:
    """
    Return the OpenAI API key without ever logging or exposing it.
    Returns None if no key is configured — caller must handle demo mode.
    """
    # 1. Try Streamlit secrets first (Community Cloud deployment)
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key and key.strip():
            return key.strip()
    except Exception:
        pass

    # 2. Fall back to environment variable (local .env / CI)
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key

    return None


def get_openai_model() -> str:
    """Return the configured model name, defaulting to gpt-4o-mini."""
    try:
        import streamlit as st
        model = st.secrets.get("OPENAI_MODEL", None)
        if model and model.strip():
            return model.strip()
    except Exception:
        pass
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()


def is_api_available() -> bool:
    """Return True if an OpenAI API key is configured."""
    return get_openai_key() is not None


def is_demo_mode() -> bool:
    """Return True when running without a real API key."""
    env_demo = os.environ.get("DEMO_MODE", "").lower()
    if env_demo == "true":
        return True
    return not is_api_available()


def get_max_web_searches() -> int:
    """Maximum web-search tool calls permitted per case analysis."""
    return 2

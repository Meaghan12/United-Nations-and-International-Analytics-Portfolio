"""
models/llm_client.py
====================
Thin wrapper for OpenAI API calls.

All calls are logged. Temperature and max_tokens are always explicitly set.
No streaming — synchronous responses only for predictability.
API key loaded from environment variable — never hardcoded.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from openai import OpenAI
    _openai_available = True
except ImportError:
    _openai_available = False


def get_llm_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0,
    max_tokens: int = 800,
    model: Optional[str] = None,
) -> str:
    """
    Send a prompt to the LLM and return the response text.

    Args:
        system_prompt: System-level instructions (role, constraints)
        user_prompt: The user-facing prompt (masked content only)
        temperature: Generation temperature (default 0 for deterministic output)
        max_tokens: Maximum response length
        model: Model identifier (defaults to env var LLM_MODEL or gpt-4o-mini)

    Returns:
        Response text string.

    Raises:
        RuntimeError: If OpenAI client is unavailable or API key is missing.
    """
    if not _openai_available:
        raise RuntimeError(
            "OpenAI package not installed. Run: pip install openai\n"
            "Or set DEMO_MODE=true to use pre-computed responses without an API key."
        )

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable not set.\n"
            "Add it to your .env file or set DEMO_MODE=true in .env "
            "to use pre-computed responses."
        )

    resolved_model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content or ""


def is_demo_mode() -> bool:
    """Check whether DEMO_MODE is set in environment."""
    return os.environ.get("DEMO_MODE", "false").lower() in ("true", "1", "yes")


def get_model_identifier() -> str:
    """Return the model identifier for audit logging."""
    if is_demo_mode():
        return "demo-mode (pre-computed)"
    return os.environ.get("LLM_MODEL", "gpt-4o-mini")

"""
LLM backend abstraction.

Selects the backend based on the ``LLM_PROVIDER`` environment variable.

Supported values:
  groq   (default)   — uses the Groq cloud API (requires GROQ_API_KEY)
  ollama             — uses a local Ollama server (no API key required)

Usage
-----
    from src.llm.llm import ask_llm, get_llm_client

    answer = ask_llm("Explain the Indian Southwest Monsoon in 3 lines.")

Environment variables
---------------------
  LLM_PROVIDER   = groq | ollama           (default: groq)
  GROQ_API_KEY   = <your key>              (required for groq)
  OLLAMA_BASE_URL= http://localhost:11434  (optional, default shown)
  OLLAMA_MODEL   = qwen3:8b                (optional, default shown)
  GROQ_MODEL     = qwen/qwen3.8-27b        (optional, default shown)
"""
import os
import logging

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


# ---------------------------------------------------------------------------
# Groq backend
# ---------------------------------------------------------------------------

def _ask_groq(prompt: str, system: str = "", temperature: float = 0.2) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------------------------
# Ollama backend (optional)
# ---------------------------------------------------------------------------

def _ask_ollama(prompt: str, system: str = "", temperature: float = 0.2) -> str:
    try:
        import requests
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as exc:
        logger.error("Ollama backend failed: %s", exc)
        raise


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_llm(
    prompt: str,
    system: str = "",
    temperature: float = 0.2,
) -> str:
    """
    Ask the configured LLM a question.

    Args:
        prompt:      User message / question
        system:      Optional system prompt
        temperature: Sampling temperature

    Returns:
        LLM response string.

    Raises:
        Exception if both backends fail.
    """
    if LLM_PROVIDER == "ollama":
        logger.info("Using Ollama backend (model=%s)", OLLAMA_MODEL)
        return _ask_ollama(prompt, system, temperature)

    # Default: Groq
    logger.info("Using Groq backend (model=%s)", GROQ_MODEL)
    return _ask_groq(prompt, system, temperature)


def get_llm_info() -> dict:
    """Return current LLM backend configuration."""
    return {
        "provider": LLM_PROVIDER,
        "model": GROQ_MODEL if LLM_PROVIDER == "groq" else OLLAMA_MODEL,
        "groq_model": GROQ_MODEL,
        "ollama_model": OLLAMA_MODEL,
        "ollama_base_url": OLLAMA_BASE_URL,
    }

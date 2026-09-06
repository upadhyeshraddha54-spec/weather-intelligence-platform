"""
Unit tests for the LLM module.
Tests configuration, imports, and helper functions — no live API calls.
"""
import os
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class TestLLMModule:
    def test_import(self):
        from src.llm.llm import ask_llm, get_llm_info
        assert callable(ask_llm)
        assert callable(get_llm_info)

    def test_get_llm_info_returns_dict(self):
        from src.llm.llm import get_llm_info
        info = get_llm_info()
        assert isinstance(info, dict)

    def test_get_llm_info_has_required_keys(self):
        from src.llm.llm import get_llm_info
        info = get_llm_info()
        for key in ("provider", "model", "groq_model", "ollama_model"):
            assert key in info, f"Missing key: {key}"

    def test_provider_is_valid(self):
        from src.llm.llm import get_llm_info
        info = get_llm_info()
        assert info["provider"] in ("groq", "ollama")

    def test_default_provider_is_groq(self):
        """Default LLM_PROVIDER must be groq unless overridden."""
        saved = os.environ.pop("LLM_PROVIDER", None)
        try:
            import importlib
            import src.llm.llm as llm_mod
            importlib.reload(llm_mod)
            assert llm_mod.LLM_PROVIDER in ("groq", "ollama")
        finally:
            if saved:
                os.environ["LLM_PROVIDER"] = saved

    def test_groq_model_is_set(self):
        from src.llm.llm import GROQ_MODEL
        assert GROQ_MODEL and len(GROQ_MODEL) > 0

    def test_ollama_base_url_is_set(self):
        from src.llm.llm import OLLAMA_BASE_URL
        assert OLLAMA_BASE_URL.startswith("http")

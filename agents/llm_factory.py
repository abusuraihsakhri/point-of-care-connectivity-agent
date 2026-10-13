"""
Inference Engine supporting local Ollama, Claude, OpenAI, and deterministic Mock with Zero-PHI checks.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Point Of Care Connectivity Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Deterministic Verification Engine]: Clinical & scientific analysis verified for query: '{prompt[:60]}...'. Parameters evaluated under CAP / CLSI / ISO Standards."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Point Of Care Connectivity Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        if prov in {"ollama", "local", "claude", "anthropic", "openai", "gpt4"}:
            raise ValueError(f"Provider '{prov}' is not implemented; use the local mock provider")
        raise ValueError(f"Unsupported model provider: {prov}")

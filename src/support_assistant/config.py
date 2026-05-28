from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

# load .env if dotenv is there
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from .llm.base import Reasoner
from .llm.rule_based import RuleBasedReasoner
from .orchestrator import SupportOrchestrator
from .router import Router
from .tools import build_default_registry

logger = logging.getLogger(__name__)


# config from env vars
@dataclass
class Settings:
    # litellm model string, eg gpt-4o-mini, groq/llama-3.1-8b-instant, ollama/llama3.1
    llm_model: str | None = field(default_factory=lambda: os.getenv("SUPPORT_LLM_MODEL"))
    # for local / openai-compatible server
    llm_api_base: str | None = field(default_factory=lambda: os.getenv("SUPPORT_LLM_API_BASE"))
    llm_api_key: str | None = field(default_factory=lambda: os.getenv("SUPPORT_LLM_API_KEY"))

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_model)


# pick llm if model is set, else offline
def build_reasoner(settings: Settings | None = None) -> Reasoner:
    settings = settings or Settings()
    if settings.llm_configured:
        try:
            from .llm import LLMReasoner  # need litellm + instructor
            logger.info("Using LLM reasoner (model=%s).", settings.llm_model)
            return LLMReasoner(
                model=settings.llm_model,
                api_base=settings.llm_api_base,
                api_key=settings.llm_api_key,
            )
        except ImportError as exc:
            # libs not installed, go offline
            logger.warning(
                "SUPPORT_LLM_MODEL is set but litellm/instructor are not "
                "installed (%s); falling back to the offline reasoner.", exc
            )
    else:
        logger.info("No SUPPORT_LLM_MODEL set; using offline rule-based reasoner.")
    return RuleBasedReasoner()


# wire everything together
def build_orchestrator(settings: Settings | None = None) -> SupportOrchestrator:
    settings = settings or Settings()
    registry = build_default_registry()
    reasoner = build_reasoner(settings)
    router = Router(reasoner=reasoner, registry=registry)
    return SupportOrchestrator(router=router, reasoner=reasoner, registry=registry)

"""FastAPI dependencies — dependency injection container for BrandOS.

All service singletons are created here and provided to routers via FastAPI's
Depends() mechanism. This file is the only place that knows which concrete
implementation backs each interface.
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from apps.api.config import Settings, get_settings
from packages.agents.service import CreativeService
from packages.evaluations.service import EvaluationService
from packages.knowledge.service import KnowledgeService
from packages.workflows.service import PlanningService


# ── KnowledgeService ──────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_knowledge_service_singleton() -> KnowledgeService:
    return KnowledgeService()


def get_knowledge_service() -> KnowledgeService:
    """Dependency provider for KnowledgeService."""
    return _get_knowledge_service_singleton()


KnowledgeServiceDep = Annotated[KnowledgeService, Depends(get_knowledge_service)]


# ── PlanningService ───────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_planning_service_singleton() -> PlanningService:
    return PlanningService()


def get_planning_service() -> PlanningService:
    """Dependency provider for PlanningService."""
    return _get_planning_service_singleton()


PlanningServiceDep = Annotated[PlanningService, Depends(get_planning_service)]


# ── Settings ──────────────────────────────────────────────────────────────────

def get_settings_dep() -> Settings:
    """Dependency provider for Settings."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


# ── CreativeService ───────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_creative_service_singleton() -> CreativeService:
    return CreativeService()


def get_creative_service() -> CreativeService:
    """Dependency provider for CreativeService."""
    return _get_creative_service_singleton()


CreativeServiceDep = Annotated[CreativeService, Depends(get_creative_service)]


# ── EvaluationService ─────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_evaluation_service_singleton() -> EvaluationService:
    return EvaluationService()


def get_evaluation_service() -> EvaluationService:
    """Dependency provider for EvaluationService."""
    return _get_evaluation_service_singleton()


EvaluationServiceDep = Annotated[EvaluationService, Depends(get_evaluation_service)]


# ── CampaignOrchestrator ──────────────────────────────────────────────────────

from packages.workflows.orchestrator import CampaignOrchestrator


def get_orchestrator() -> CampaignOrchestrator:
    """Build an Orchestrator that shares the same service singletons.

    We do NOT use lru_cache here because CampaignOrchestrator holds no
    state — it only delegates to the three underlying singletons. Creating
    it fresh per request is effectively free.
    """
    return CampaignOrchestrator(
        planning_service=_get_planning_service_singleton(),
        creative_service=_get_creative_service_singleton(),
        evaluation_service=_get_evaluation_service_singleton(),
    )


OrchestratorDep = Annotated[CampaignOrchestrator, Depends(get_orchestrator)]

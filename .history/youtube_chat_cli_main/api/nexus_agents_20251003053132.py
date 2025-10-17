"""
FastAPI router for Nexus Agents (scaffold)

Provides minimal endpoints that call the workflow scaffolds.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..workflows import deep_research, content_checks

router = APIRouter()


class DeepResearchRequest(BaseModel):
    topic: str
    max_turns: Optional[int] = None
    backends: Optional[List[str]] = None


@router.post("/deep-research")
async def api_deep_research(req: DeepResearchRequest) -> Dict[str, Any]:
    return deep_research.run(topic=req.topic, max_turns=req.max_turns, backends=req.backends)


class ContentCheckRequest(BaseModel):
    topic: str
    max_loops: Optional[int] = None


@router.post("/content-check")
async def api_content_check(req: ContentCheckRequest) -> Dict[str, Any]:
    return content_checks.run(topic=req.topic, max_loops=req.max_loops)


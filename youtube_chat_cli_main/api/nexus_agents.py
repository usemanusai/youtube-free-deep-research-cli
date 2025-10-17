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



from fastapi import HTTPException, Query, Path
from pydantic import BaseModel, Field
import uuid as _uuid
from ..core.database import get_database
from ..services.background_service import get_background_service

class SessionsListResponse(BaseModel):
    sessions: list[dict]
    total: int
    limit: int
    offset: int

@router.get("/sessions", response_model=SessionsListResponse)
async def list_sessions(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), workflow_type: str | None = Query(None)):
    db = get_database()
    res = db.list_sessions(limit=limit, offset=offset, workflow_type=workflow_type)
    return SessionsListResponse(**res)

class SessionDetailResponse(BaseModel):
    session: dict
    messages: list[dict]

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str = Path(...)):
    try:
        _ = _uuid.UUID(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    db = get_database()
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = db.get_session_messages(session_id)
    return SessionDetailResponse(session=session, messages=msgs)

class ArchiveStatusResponse(BaseModel):
    total_vectors: int
    gdrive_vectors: int
    last_sync_time: str | None
    indexing_status: str
    files_indexed: int
    files_pending: int | None

@router.get("/archive/status", response_model=ArchiveStatusResponse)
async def archive_status():
    svc = get_background_service()
    return ArchiveStatusResponse(**svc.get_indexing_status())

class ReindexRequest(BaseModel):
    force: bool = Field(default=False)

class ReindexResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/archive/reindex", response_model=ReindexResponse)
async def archive_reindex(req: ReindexRequest):
    svc = get_background_service()
    job_id = svc.start_reindex_job(force=req.force)
    return ReindexResponse(job_id=job_id, status="started", message="Reindex job started")


class QueueBreakdownResponse(BaseModel):
    total: int
    by_status: dict
    by_source: dict
    by_file_type: dict
    by_age: dict
    by_retry_count: dict

@router.get("/archive/queue", response_model=QueueBreakdownResponse)
async def archive_queue_breakdown():
    db = get_database()
    data = db.get_queue_breakdown()
    return QueueBreakdownResponse(**data)


# --- Observability: Workflow traces ---
class WorkflowTraceItem(BaseModel):
    workflow_id: str
    workflow_type: str
    stage: str
    state: dict
    created_at: str

class WorkflowTraceResponse(BaseModel):
    workflow_id: str
    traces: list[WorkflowTraceItem]

@router.get("/workflows/{workflow_id}/trace", response_model=WorkflowTraceResponse)
async def get_workflow_trace(workflow_id: str = Path(...)):
    db = get_database()
    items = db.get_workflow_traces(workflow_id)
    return WorkflowTraceResponse(workflow_id=workflow_id, traces=[WorkflowTraceItem(**i) for i in items])

# --- Batch processing endpoint ---
class BatchResearchRequest(BaseModel):
    topics: List[str]
    max_turns: Optional[int] = None

class BatchResearchItem(BaseModel):
    topic: str
    result: Dict[str, Any]

class BatchResearchResponse(BaseModel):
    items: List[BatchResearchItem]

@router.post("/batch-research", response_model=BatchResearchResponse)
async def batch_research(req: BatchResearchRequest):
    out: List[BatchResearchItem] = []
    for t in req.topics[:50]:  # cap to 50 per request
        try:
            res = deep_research.run(topic=t, max_turns=req.max_turns)
        except Exception as e:
            res = {"error": str(e)}
        out.append(BatchResearchItem(topic=t, result=res))
    return BatchResearchResponse(items=out)

# --- Circuit breaker health ---
class CircuitBreakerHealth(BaseModel):
    name: str
    open: bool
    opened_until: float
    failures: int

class CircuitBreakersResponse(BaseModel):
    breakers: list[CircuitBreakerHealth]

@router.get("/health/circuit-breakers", response_model=CircuitBreakersResponse)
async def cb_health():
    try:
        from ..core.circuit_health import snapshot
        snap = snapshot()
        items = [CircuitBreakerHealth(name=k, open=v["open"], opened_until=v["opened_until"], failures=v["failures"]) for k, v in snap.items()]
        return CircuitBreakersResponse(breakers=items)
    except Exception:
        return CircuitBreakersResponse(breakers=[])


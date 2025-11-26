from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import load_config
from .agents.president import BathyPresident
from .agents.clerk import Clerk
from .agents.janitor import Janitor
from .tools import TOOL_REGISTRY
from .memory_backend import MemoryBackend
from .automation import AutomationEngine
from .user_profile import get_store as get_user_profile_store
from .teachings import get_store as get_teaching_store
from .brain import get_brain_blueprint
from .action_queue import enqueue_actions


class ChatRequest(BaseModel):
    message: str
    agent_selector: Optional[str] = None
    max_tokens: Optional[int] = None
    mode: Optional[str] = None


class ToolExecRequest(BaseModel):
    name: str
    args: Dict[str, Any]
    consent_token: Optional[str] = None


class ToolExecResponse(BaseModel):
    ok: bool
    detail: str
    result: Dict[str, Any]


class AgentTraceItem(BaseModel):
    agent: str
    role: str
    proposal: str


class SuggestedAction(BaseModel):
    kind: str  # e.g. "tool" | "note" | "automation_idea"
    description: str
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    output: str
    used_model: str
    agent_trace: List[AgentTraceItem]
    suggested_actions: List[SuggestedAction] = []


class TeachRequest(BaseModel):
    topic: str
    instruction: str
    tags: Optional[List[str]] = None


class TeachResponse(BaseModel):
    topic: str
    instruction: str
    tags: List[str]
    created_at: str


class AutomationTaskPayload(BaseModel):
    id: str
    name: str
    enabled: bool = True
    kind: str = "interval"  # "once" or "interval"
    next_run_at: Optional[str] = None
    interval_seconds: Optional[int] = None
    steps: List[Dict[str, Any]]


app = FastAPI(title="GoodBoy.AI Bathy Core", version="0.1.0")

bathy = BathyPresident()
clerk = Clerk()
janitor = Janitor()
memory_backend = MemoryBackend()automation_engine = AutomationEngine()
_user_profile_store = get_user_profile_store()
_teaching_store = get_teaching_store()


@app.get("/")
async def root() -> Dict[str, Any]:
    cfg = load_config()
    return {
        "status": "ok",
        "engine": cfg.get("engine", "local"),
        "model_path": cfg.get("model_path"),
        "safety_mode": cfg.get("safety_mode", "interactive"),
        "agents": bathy.list_agents(),
        "allowed_tools": cfg.get("allowed_tools", []),
    }


@app.get("/agents")
async def list_agents() -> Dict[str, Any]:
    """List advisor agents Bathy can call on."""
    return {"agents": bathy.list_agents()}


@app.get("/brain/blueprint")
async def brain_blueprint() -> Dict[str, Any]:
    """Return an introspectable chain-of-command map for GoodBoy.AI City."""
    return get_brain_blueprint()


@app.get("/memory/search")
async def memory_search(q: str, k: int = 5) -> Dict[str, Any]:
    """Search GoodBoy.AI long-term memory for relevant context."""
    results = memory_backend.search(q, k=k)
    return {"query": q, "results": results}


@app.post("/teach", response_model=TeachResponse)
async def teach(req: TeachRequest) -> TeachResponse:
    """Explicitly teach Bathy a lesson.

    Lessons are stored in data/teachings.jsonl and also offered to the
    MemoryBackend for retrieval.
    """

    lesson = _teaching_store.add_lesson(req.topic, req.instruction, req.tags)
    # Offer lesson into vector memory as well.
    memory_backend.ingest_items(
        [
            {
                "id": f"teaching-{hash((lesson.topic, lesson.created_at))}",
                "text": f"Teaching topic: {lesson.topic}\nInstruction: {lesson.instruction}",
                "meta": {"source": "teaching", "tags": lesson.tags},
            }
        ]
    )
    return TeachResponse(
        topic=lesson.topic,
        instruction=lesson.instruction,
        tags=lesson.tags,
        created_at=lesson.created_at,
    )


@app.post("/janitor/run")
async def janitor_run() -> Dict[str, Any]:
    rep = janitor.run_checks()
    return {"ok": rep.ok, "summary": rep.summary, "details": rep.details}


@app.get("/janitor/status")
async def janitor_status() -> Dict[str, Any]:
    return janitor.last_status()


# --- Automation endpoints ----------------------------------------------------


@app.get("/automation/tasks")
async def list_automation_tasks() -> Dict[str, Any]:
    return {"tasks": automation_engine.list_tasks()}


@app.post("/automation/tasks")
async def upsert_automation_task(payload: AutomationTaskPayload) -> Dict[str, Any]:
    task = automation_engine.upsert_task(payload.dict())
    return {"task": task.to_dict()}


@app.delete("/automation/tasks/{task_id}")
async def delete_automation_task(task_id: str) -> Dict[str, Any]:
    removed = automation_engine.delete_task(task_id)
    return {"removed": removed}


@app.post("/automation/run-due")
async def automation_run_due() -> Dict[str, Any]:
    rep = automation_engine.run_due_tasks()
    return rep


@app.post("/tools/exec", response_model=ToolExecResponse)
async def tools_exec(req: ToolExecRequest) -> ToolExecResponse:
    cfg = load_config()
    if req.name not in cfg.get("allowed_tools", []):
        raise HTTPException(status_code=403, detail=f"Tool '{req.name}' is not allowed.")

    result = clerk.execute(req.name, req.args, consent_token=req.consent_token)
    # Self-learning hook: record tool outcome in user profile.
    _user_profile_store.record_tool(req.name, result.ok, result.detail)
    return ToolExecResponse(ok=result.ok, detail=result.detail, result=result.tool_result.data)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        result = bathy.handle(req.message, agent_selector=req.agent_selector, max_tokens=req.max_tokens)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Model inference error: {e}")

    trace_items = [AgentTraceItem(agent=p.agent, role=p.role, proposal=p.proposal) for p in result.trace]
    # All advisors share the same underlying model for now (Qwen/TinyLlama via GPT4All)
    from .models_backend import ModelBackend  # local import to avoid circulars at import time

    backend = ModelBackend.instance()
    used_model_path = str(backend.model_path)

    # Optional: ask the model for structured suggested actions.
    suggested_actions: List[SuggestedAction] = []
    try:
        tools_list = ", ".join(load_config().get("allowed_tools", []))
        planner_prompt = (
            "You are Bathy, planning potential follow-up actions for the owner's request. "
            "You have access to tools with these names: "
            f"{tools_list}. Given the user's request and your reply, propose at most 3 "
            "actions as JSON. Use a list of objects with keys 'kind', 'description', "
            "'tool_name', and 'tool_args'. 'kind' can be 'tool', 'note', or 'automation_idea'. "
            "If no actions are appropriate, return an empty JSON list.\n\n"
            f"User request: {req.message}\n"
            f"Bathy reply: {result.output}\n"
        )
        raw_plan = backend.generate(planner_prompt, max_tokens=256, temperature=0.2)
        import json as _json

        parsed = _json.loads(raw_plan.strip()) if raw_plan.strip().startswith("[") else []
        for item in parsed:
            try:
                suggested_actions.append(
                    SuggestedAction(
                        kind=str(item.get("kind", "note")),
                        description=str(item.get("description", "")),
                        tool_name=item.get("tool_name"),
                        tool_args=item.get("tool_args") or {},
                    )
                )
            except Exception:
                continue
    except Exception:
        suggested_actions = []

    # Self-learning hook: record chat for the owner profile, and optionally
    # feed into long-term memory if configured.
    _user_profile_store.record_chat(req.message, result.output)
    cfg = load_config()
    if cfg.get("memory_auto_ingest_from_api", True):
        memory_backend.ingest_items(
            [
                {
                    "id": f"api-chat-{hash((req.message, result.output))}",
                    "text": f"User: {req.message}\nAssistant: {result.output}",
                    "meta": {"source": "api_chat", "agent_selector": req.agent_selector or "council"},
                }
            ]
        )

    # Enqueue suggested actions for later processing by autonomous scripts.
    try:
        enqueue_actions(
            [
                {
                    "kind": sa.kind,
                    "description": sa.description,
                    "tool_name": sa.tool_name,
                    "tool_args": sa.tool_args,
                }
                for sa in suggested_actions
            ],
            source_message=req.message,
            source_reply=result.output,
        )
    except Exception:
        # Queueing should never break the main chat path.
        pass

    return ChatResponse(
        output=result.output,
        used_model=used_model_path,
        agent_trace=trace_items,
        suggested_actions=suggested_actions,
    )

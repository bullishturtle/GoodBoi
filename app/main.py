"""GoodBoy.AI FastAPI Backend - The Bathy City Server with Unified Brain."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime
from pathlib import Path

from app.council import CouncilRouter
from app.memory import MemoryManager
from app.models import ChatRequest, ChatResponse, TeachingRequest
from app.memory_evolution import EvolutionSystem
from app.learning_engine import LearningEngine
from app.mini_bot_nursery import MiniBotNursery
from app.teachings import get_store
from app.brain import get_brain, UnifiedBrain
from app.widgets import WidgetManager, SystemStats

# Initialize directories
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
MEMORY_DIR = Path("memory")
for d in [DATA_DIR, MODELS_DIR, MEMORY_DIR]:
    d.mkdir(exist_ok=True)

# Global instances
council = None
memory_manager = None
evolution_system = None
learning_engine = None
minibot_nursery = None
brain: UnifiedBrain = None
widget_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown."""
    global council, memory_manager, evolution_system, learning_engine, minibot_nursery, brain, widget_manager
    
    print("[GoodBoy.AI] Initializing Bathy City systems...")
    
    brain = get_brain()
    print(f"[GoodBoy.AI] Brain online - {brain.get_introspection()}")
    
    council = CouncilRouter()
    memory_manager = MemoryManager(MEMORY_DIR)
    evolution_system = EvolutionSystem(MEMORY_DIR)
    learning_engine = LearningEngine(MEMORY_DIR)
    minibot_nursery = MiniBotNursery(MEMORY_DIR)
    widget_manager = WidgetManager()
    
    print("[GoodBoy.AI] Council online with agents:", [a.name for a in council.agents])
    print("[GoodBoy.AI] Memory, Evolution, and Learning systems active")
    print("[GoodBoy.AI] Widget dashboard ready")
    print("[GoodBoy.AI] Bathy City is ready to serve!")
    
    yield
    
    print("[GoodBoy.AI] Shutting down Bathy City...")


app = FastAPI(
    title="GoodBoy.AI",
    description="Self-aware, self-learning AI assistant with unified brain architecture",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for desktop UI and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check and system status."""
    return {
        "status": "ok",
        "app": "GoodBoy.AI",
        "version": "1.0.0",
        "agents": [a.name for a in council.agents] if council else [],
        "brain_status": brain.get_status() if brain else None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/status")
async def status():
    """Detailed system status."""
    return {
        "status": "online",
        "version": "1.0.0",
        "agents_count": len(council.agents) if council else 0,
        "memory_entries": len(memory_manager.messages) if memory_manager else 0,
        "brain": brain.get_status() if brain else None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/brain/introspect")
async def brain_introspect():
    """Get brain's self-reflection and current state."""
    if not brain:
        raise HTTPException(status_code=503, detail="Brain not initialized")
    
    return {
        "introspection": brain.get_introspection(),
        "status": brain.get_status(),
        "thought_trace": brain.get_thought_trace()
    }


@app.get("/brain/thoughts")
async def get_thoughts():
    """Get recent chain-of-thought history."""
    if not brain:
        raise HTTPException(status_code=503, detail="Brain not initialized")
    
    return {
        "current_state": brain.self_awareness.current_state.value,
        "recent_thoughts": [
            {
                "query": cot.query[:100],
                "confidence": cot.confidence,
                "agents": cot.agents_consulted,
                "emotional_tone": cot.emotional_tone.value,
                "reasoning_time_ms": cot.reasoning_time_ms,
                "thought_count": len(cot.thoughts)
            }
            for cot in brain.thought_history[-10:]
        ]
    }


@app.get("/evolution")
async def evolution():
    """Get evolution status for UI."""
    if evolution_system:
        return evolution_system.get_status()
    return {"generation": 0, "total_interactions": 0}


@app.get("/agents")
async def list_agents():
    """List all available agents in the council."""
    return {
        "agents": [
            {
                "name": a.name,
                "role": a.role,
                "description": a.description,
                "status": a.get_status()
            }
            for a in council.agents
        ]
    }


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint - routes through unified brain."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Store user message
    memory_manager.add_message(user_message=request.message)
    
    try:
        response_text, chain_of_thought = await brain.think(
            query=request.message,
            context=memory_manager.get_context(),
            council=council,
            memory_manager=memory_manager,
            evolution_system=evolution_system,
            learning_engine=learning_engine
        )
    except Exception as e:
        # Fallback to direct council if brain fails
        result = await council.process(
            message=request.message,
            mode=request.mode or "auto",
            context=memory_manager.get_context()
        )
        response_text = result["output"]
        chain_of_thought = None
    
    # Store response
    memory_manager.add_message(assistant_message=response_text)
    
    # Check if mini-bot should be spawned for repeated patterns
    if learning_engine and learning_engine.suggest_routing_optimization():
        opt = learning_engine.suggest_routing_optimization()
        if opt and opt.get("frequency", 0) > 5:
            keywords = request.message.lower().split()[:3]
            minibot_nursery.spawn_minibot(
                specialization=f"Pattern: {keywords}",
                parent_agent=opt["suggested_agents"][0] if opt["suggested_agents"] else "Jarvis",
                trigger_pattern=" ".join(keywords)
            )
    
    return ChatResponse(
        output=response_text,
        agent_trace=[
            {"agent": t.source, "proposal": t.content, "confidence": t.confidence}
            for t in (chain_of_thought.thoughts if chain_of_thought else [])
        ],
        route_metadata={
            "mode": "brain",
            "agents": chain_of_thought.agents_consulted if chain_of_thought else [],
            "confidence": chain_of_thought.confidence if chain_of_thought else 0.5,
            "emotional_tone": chain_of_thought.emotional_tone.value if chain_of_thought else "neutral",
            "reasoning_time_ms": chain_of_thought.reasoning_time_ms if chain_of_thought else 0
        },
        suggested_actions=[]
    )


@app.get("/memory/search")
async def search_memory(q: str, k: int = 5):
    """Search memory with keyword matching."""
    results = memory_manager.search(query=q, k=k)
    return {"query": q, "results": results}


@app.get("/memory/context")
async def get_context(k: int = 10):
    """Get recent conversation context."""
    return memory_manager.get_context(k=k)


@app.post("/teachings/add")
async def add_teaching(request: TeachingRequest):
    """Add a new teaching/lesson to GoodBoy's knowledge."""
    store = get_store()
    lesson = store.add_lesson(
        topic=request.topic,
        instruction=request.instruction,
        tags=request.tags or [],
        source="user"
    )
    return {"status": "added", "lesson_id": lesson.id}


@app.get("/teachings/search")
async def search_teachings(q: str, k: int = 5):
    """Search teachings by query."""
    store = get_store()
    lessons = store.get_relevant_lessons(q, k=k)
    return {
        "query": q,
        "lessons": [
            {
                "id": l.id,
                "topic": l.topic,
                "instruction": l.instruction,
                "tags": l.tags,
                "effectiveness": l.effectiveness_score
            }
            for l in lessons
        ]
    }


@app.post("/janitor/run")
async def run_janitor():
    """Run health checks and cleanup."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "memory_entries": len(memory_manager.messages),
        "agents_healthy": len([a for a in council.agents if a.is_healthy()]),
        "evolution_status": evolution_system.get_status(),
        "brain_status": brain.get_status() if brain else None,
        "minibots_active": len(minibot_nursery.get_active_minibots()),
        "actions": []
    }
    
    # Memory cleanup (keep last 30 days)
    old_count = len(memory_manager.messages)
    memory_manager.cleanup_old_entries(days=30)
    cleaned = old_count - len(memory_manager.messages)
    if cleaned > 0:
        report["actions"].append(f"Cleaned {cleaned} old memory entries")
    
    # Brain rest (restore energy)
    if brain:
        brain.self_awareness.rest()
        report["actions"].append("Brain rested - energy restored")
    
    # Generate evolution suggestions
    suggestions = evolution_system.suggest_actions()
    report["overseer_suggestions"] = suggestions
    
    return report


@app.get("/evolution/status")
async def get_evolution_status():
    """Get detailed evolution status."""
    return evolution_system.get_status()


@app.post("/evolution/generate")
async def trigger_generation():
    """Manually trigger new evolutionary generation."""
    gen_info = evolution_system.trigger_generation_increment()
    return {
        "message": "New generation triggered",
        "generation_info": gen_info
    }


@app.get("/minibots/list")
async def list_minibots():
    """List all active mini-bots."""
    bots = minibot_nursery.get_active_minibots()
    return {
        "minibots": bots,
        "count": len(bots)
    }


@app.post("/minibots/spawn")
async def spawn_minibot(specialization: str, parent_agent: str, trigger_pattern: str):
    """Manually spawn a new mini-bot."""
    minibot = minibot_nursery.spawn_minibot(
        specialization=specialization,
        parent_agent=parent_agent,
        trigger_pattern=trigger_pattern
    )
    return {"message": "Mini-bot spawned", "minibot": minibot}


@app.get("/widgets/system")
async def get_system_widget():
    """Get system monitoring widget data."""
    return widget_manager.get_system_widget()


@app.get("/widgets/brain")
async def get_brain_widget():
    """Get brain status widget."""
    return widget_manager.get_brain_widget(brain)


@app.get("/widgets/agents")
async def get_agents_widget():
    """Get council agents widget."""
    return widget_manager.get_agent_widget(council.agents if council else [])


@app.get("/widgets/evolution")
async def get_evolution_widget():
    """Get evolution tracker widget."""
    return widget_manager.get_evolution_widget(evolution_system)


@app.get("/widgets/thoughts")
async def get_thoughts_widget():
    """Get chain-of-thought visualizer widget."""
    return widget_manager.get_thought_widget(brain)


@app.get("/widgets/all")
async def get_all_widgets():
    """Get all widgets at once for dashboard."""
    return {
        "system": widget_manager.get_system_widget(),
        "brain": widget_manager.get_brain_widget(brain),
        "agents": widget_manager.get_agents_widget(council.agents if council else []),
        "evolution": widget_manager.get_evolution_widget(evolution_system),
        "thoughts": widget_manager.get_thought_widget(brain),
        "uptime": widget_manager.get_uptime()
    }


@app.get("/widgets/uptime")
async def get_uptime():
    """Get system uptime."""
    return {
        "uptime": widget_manager.get_uptime(),
        "timestamp": datetime.now().isoformat()
    }

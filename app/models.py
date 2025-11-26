"""Pydantic models for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=8000)
    mode: Optional[str] = Field(None, pattern="^(auto|reflex|council|strategic)$")
    context: Optional[Dict[str, Any]] = None


class ThoughtStep(BaseModel):
    """Single step in chain-of-thought reasoning."""
    source: str
    content: str
    confidence: float


class AgentTrace(BaseModel):
    """Agent response in trace."""
    agent: str
    proposal: str
    confidence: Optional[float] = 0.7
    timestamp: Optional[str] = None


class RouteMetadata(BaseModel):
    """Routing metadata with brain integration."""
    mode: str
    agents: List[str]
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    emotional_tone: Optional[str] = None
    reasoning_time_ms: Optional[int] = None


class SuggestedAction(BaseModel):
    """Suggested action for user."""
    kind: str
    description: str
    tool_name: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    output: str
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list)
    route_metadata: Dict[str, Any] = Field(default_factory=dict)
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)


class TeachingRequest(BaseModel):
    """Request to add a teaching/lesson."""
    topic: str
    instruction: str
    tags: Optional[List[str]] = None


class EvolutionStatus(BaseModel):
    """Evolution system status."""
    generation: int
    total_interactions: int
    success_rate: float
    agent_proficiency: Dict[str, float]
    timestamp: str


class BrainStatus(BaseModel):
    """Brain's self-awareness status."""
    identity: str
    state: str
    mood: str
    confidence: float
    energy: float
    total_thoughts: int
    success_rate: float
    personality: Dict[str, float]
    core_beliefs: List[str]
    strengths: List[str]
    weaknesses: List[str]


class IntrospectionResponse(BaseModel):
    """Response from brain introspection."""
    introspection: str
    status: BrainStatus
    thought_trace: Optional[str] = None

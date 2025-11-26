"""Base Agent class with chain-of-thought reasoning and self-awareness."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

try:
    from app.llm import generate_with_system, is_available, get_error
    LLM_IMPORT_ERROR = None
except Exception as e:
    logging.error(f"Failed to import LLM module: {e}")
    LLM_IMPORT_ERROR = str(e)
    
    def generate_with_system(*args, **kwargs):
        return f"[LLM Error] {LLM_IMPORT_ERROR}"
    def is_available():
        return False
    def get_error():
        return LLM_IMPORT_ERROR

try:
    from app.tools import get_tool_registry, ToolResult
except Exception:
    def get_tool_registry():
        return None
    ToolResult = dict


@dataclass
class AgentThought:
    """A single thought in the agent's reasoning process."""
    step: int
    content: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentReasoning:
    """Complete reasoning chain for an agent's response."""
    thoughts: List[AgentThought] = field(default_factory=list)
    conclusion: str = ""
    total_confidence: float = 0.0
    
    def add_step(self, content: str, confidence: float = 0.7):
        """Add a reasoning step."""
        step = AgentThought(
            step=len(self.thoughts) + 1,
            content=content,
            confidence=confidence
        )
        self.thoughts.append(step)
        return step
    
    def finalize(self, conclusion: str):
        """Finalize reasoning with conclusion."""
        self.conclusion = conclusion
        if self.thoughts:
            self.total_confidence = sum(t.confidence for t in self.thoughts) / len(self.thoughts)
    
    def get_trace(self) -> str:
        """Get human-readable reasoning trace."""
        lines = [f"Step {t.step}: {t.content} (confidence: {t.confidence:.0%})" for t in self.thoughts]
        lines.append(f"Conclusion: {self.conclusion}")
        return "\n".join(lines)


class BaseAgent(ABC):
    """Base class for all council agents with chain-of-thought reasoning."""
    
    COT_WRAPPER = """You are {name}, the {role} specialist in GoodBoy.AI's council.

IMPORTANT: Think step-by-step before responding. Structure your thinking as:

<Thinking>
1. What is being asked?
2. What knowledge/tools do I have for this?
3. What are the key considerations?
4. What's my recommendation?
</Thinking>

<response>
Your actual response here.
</response>

{system_prompt}

Remember: You are part of a council. Your perspective matters but will be synthesized with others.
Be concise, specific, and confident in your domain expertise."""

    def __init__(self, name: str, role: str, description: str, system_prompt: str):
        self.name = name
        self.role = role
        self.description = description
        self._base_system_prompt = system_prompt
        self.system_prompt = self.COT_WRAPPER.format(
            name=name,
            role=role,
            system_prompt=system_prompt
        )
        self.is_active = True
        try:
            self.tools = get_tool_registry()
        except Exception:
            self.tools = None
        
        self.proficiency_score = 0.5
        self.interactions = 0
        self.successful_interactions = 0
        self.current_reasoning: Optional[AgentReasoning] = None
        
        # Agent's self-model
        self.self_model = {
            "strengths": [],
            "weaknesses": [],
            "preferred_query_types": [],
            "last_performance": 0.5
        }
    
    @abstractmethod
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate proposal for handling message."""
        pass
    
    def think(self, message: str, context: Optional[str] = None) -> str:
        """Use LLM with chain-of-thought reasoning."""
        if not is_available():
            error_msg = get_error() or "LLM not available"
            return f"[{self.name}] Cannot process: {error_msg}"
        
        self.current_reasoning = AgentReasoning()
        self.current_reasoning.add_step(f"Received query: {message[:100]}...", 0.9)
        
        try:
            response = generate_with_system(
                system_prompt=self.system_prompt,
                user_message=message,
                context=context,
                max_tokens=512,
                temperature=0.6
            )
            
            thinking, actual_response = self._parse_cot_response(response)
            
            if thinking:
                self.current_reasoning.add_step(f"Internal reasoning: {thinking[:200]}...", 0.8)
            
            self.current_reasoning.finalize(actual_response)
            return actual_response
            
        except Exception as e:
            self.current_reasoning.add_step(f"Error occurred: {str(e)}", 0.2)
            return f"[{self.name}] Error generating response: {str(e)}"
    
    def _parse_cot_response(self, response: str) -> tuple:
        """Parse thinking and response from chain-of-thought output."""
        thinking = ""
        actual_response = response
        
        # Try to extract <Thinking> and <response> blocks
        if "<Thinking>" in response and "</Thinking>" in response:
            start = response.find("<Thinking>") + len("<Thinking>")
            end = response.find("</Thinking>")
            thinking = response[start:end].strip()
        
        if "<response>" in response and "</response>" in response:
            start = response.find("<response>") + len("<response>")
            end = response.find("</response>")
            actual_response = response[start:end].strip()
        elif "<Thinking>
</Thinking>" in response:
            # Response is everything after thinking
            actual_response = response.split("<Thinking>
</Thinking>")[-1].strip()
        
        return thinking, actual_response
    
    def use_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool."""
        if not self.tools:
            return {"error": "Tool registry not available", "success": False}
        return self.tools.execute(tool_name, **kwargs)
    
    def is_healthy(self) -> bool:
        """Check if agent is operational."""
        return self.is_active and is_available()
    
    def record_outcome(self, was_successful: bool):
        """Track agent performance with self-reflection."""
        self.interactions += 1
        if was_successful:
            self.successful_interactions += 1
        
        # Update proficiency with momentum
        delta = 0.05 if was_successful else -0.03
        self.proficiency_score = max(0.1, min(1.0, self.proficiency_score + delta))
        self.self_model["last_performance"] = 1.0 if was_successful else 0.0
    
    def get_reasoning_trace(self) -> Optional[str]:
        """Get current reasoning trace."""
        if self.current_reasoning:
            return self.current_reasoning.get_trace()
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status including self-awareness."""
        success_rate = self.successful_interactions / max(self.interactions, 1)
        return {
            "name": self.name,
            "role": self.role,
            "active": self.is_active,
            "proficiency": round(self.proficiency_score, 2),
            "interactions": self.interactions,
            "success_rate": round(success_rate, 2),
            "llm_available": is_available(),
            "self_model": self.self_model
        }
    
    def _format_response(self, content: str, level: str = "info") -> str:
        """Format agent response."""
        return content  # Clean output without prefix

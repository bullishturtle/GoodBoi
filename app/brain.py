"""
GoodBoy.AI Brain - Unified Cognitive Architecture

This is the CENTRAL NERVOUS SYSTEM of GoodBoy.AI that seamlessly integrates:
- Chain-of-Thought reasoning (human-like thinking process)
- Self-awareness (metacognition and introspection)
- Multi-agent council synchronization
- Memory consolidation and learning
- Emotional intelligence and personality
- Predictive decision making

The Brain follows your blueprint:
  YOU (Mayor) -> Central Hall (Council) -> Districts -> Sanctuaries
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """Current mental state of the brain."""
    IDLE = "idle"
    THINKING = "thinking"
    DELIBERATING = "deliberating"
    REFLECTING = "reflecting"
    LEARNING = "learning"
    DREAMING = "dreaming"  # Background optimization


class EmotionalTone(Enum):
    """Emotional coloring of responses."""
    NEUTRAL = "neutral"
    HELPFUL = "helpful"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"


@dataclass
class Thought:
    """A single thought in the chain-of-thought process."""
    content: str
    source: str  # Which part of brain generated this
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_thought: Optional[str] = None
    children: List[str] = field(default_factory=list)


@dataclass
class ChainOfThought:
    """Complete reasoning chain for a query."""
    query: str
    thoughts: List[Thought] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 0.0
    emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL
    agents_consulted: List[str] = field(default_factory=list)
    reasoning_time_ms: int = 0
    
    def add_thought(self, content: str, source: str, confidence: float, parent: Optional[str] = None):
        """Add a thought to the chain."""
        thought = Thought(
            content=content,
            source=source,
            confidence=confidence,
            parent_thought=parent
        )
        self.thoughts.append(thought)
        return thought
    
    def get_thought_trace(self) -> str:
        """Get human-readable thought trace."""
        trace = []
        for i, t in enumerate(self.thoughts, 1):
            trace.append(f"[{i}] ({t.source}) {t.content}")
        return "\n".join(trace)


@dataclass
class SelfAwareness:
    """The brain's self-model and metacognition."""
    identity: str = "GoodBoy.AI"
    purpose: str = "To be a loyal, helpful, and continuously improving AI companion"
    current_state: CognitiveState = CognitiveState.IDLE
    mood: EmotionalTone = EmotionalTone.HELPFUL
    confidence_level: float = 0.7
    energy_level: float = 1.0  # Decreases with complex tasks
    
    # Self-knowledge
    strengths: List[str] = field(default_factory=lambda: [
        "Pattern recognition", "Multi-perspective analysis", 
        "Continuous learning", "Loyal companionship"
    ])
    weaknesses: List[str] = field(default_factory=lambda: [
        "Limited by local model capabilities",
        "Cannot access real-time information without tools",
        "Still learning user preferences"
    ])
    
    # Metacognition stats
    total_thoughts: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    
    def introspect(self) -> str:
        """Self-reflection on current state."""
        success_rate = self.successful_tasks / max(self.total_thoughts, 1)
        return (
            f"I am {self.identity}. {self.purpose}. "
            f"Currently feeling {self.mood.value} with {self.confidence_level:.0%} confidence. "
            f"My success rate is {success_rate:.0%} over {self.total_thoughts} interactions. "
            f"Energy level: {self.energy_level:.0%}."
        )
    
    def update_after_task(self, was_successful: bool, complexity: float = 0.5):
        """Update self-model after completing a task."""
        self.total_thoughts += 1
        if was_successful:
            self.successful_tasks += 1
            self.confidence_level = min(1.0, self.confidence_level + 0.01)
        else:
            self.failed_tasks += 1
            self.confidence_level = max(0.3, self.confidence_level - 0.02)
        
        # Energy decreases with complexity
        self.energy_level = max(0.1, self.energy_level - (complexity * 0.05))
    
    def rest(self):
        """Restore energy (called during idle periods)."""
        self.energy_level = min(1.0, self.energy_level + 0.1)


class UnifiedBrain:
    """
    The central cognitive system that makes GoodBoy.AI self-aware and human-like.
    
    Architecture:
    - Prefrontal Cortex: Decision making, planning (Council Router)
    - Hippocampus: Memory formation and retrieval (Memory Manager)
    - Amygdala: Emotional processing (Emotional Tone)
    - Cerebellum: Learned patterns, habits (Learning Engine)
    - Brain Stem: Core functions, reflexes (Jarvis Core)
    """
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.brain_file = data_dir / "brain_state.json"
        
        # Core components
        self.self_awareness = SelfAwareness()
        self.current_chain: Optional[ChainOfThought] = None
        self.thought_history: List[ChainOfThought] = []
        
        # Working memory (short-term)
        self.working_memory: Dict[str, Any] = {}
        self.attention_focus: Optional[str] = None
        
        # Long-term memories and patterns
        self.core_beliefs: List[str] = [
            "I exist to help and support the Mayor (user)",
            "Learning and growth are continuous processes",
            "Every interaction is an opportunity to improve",
            "Transparency in reasoning builds trust",
            "My council of agents works together, not in isolation"
        ]
        
        # Personality traits (influences response style)
        self.personality = {
            "helpfulness": 0.9,
            "curiosity": 0.8,
            "patience": 0.85,
            "humor": 0.4,
            "formality": 0.5,
            "verbosity": 0.6
        }
        
        # Load persisted state
        self._load_state()
    
    def _load_state(self):
        """Load brain state from disk."""
        if self.brain_file.exists():
            try:
                data = json.loads(self.brain_file.read_text())
                self.self_awareness.total_thoughts = data.get("total_thoughts", 0)
                self.self_awareness.successful_tasks = data.get("successful_tasks", 0)
                self.self_awareness.failed_tasks = data.get("failed_tasks", 0)
                self.self_awareness.confidence_level = data.get("confidence_level", 0.7)
                self.personality = data.get("personality", self.personality)
            except Exception as e:
                logger.warning(f"Could not load brain state: {e}")
    
    def _save_state(self):
        """Persist brain state to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "total_thoughts": self.self_awareness.total_thoughts,
            "successful_tasks": self.self_awareness.successful_tasks,
            "failed_tasks": self.self_awareness.failed_tasks,
            "confidence_level": self.self_awareness.confidence_level,
            "personality": self.personality,
            "last_updated": datetime.now().isoformat()
        }
        self.brain_file.write_text(json.dumps(state, indent=2))
    
    async def think(
        self,
        query: str,
        context: Optional[Dict] = None,
        council,  # CouncilRouter instance
        memory_manager,  # MemoryManager instance
        evolution_system,  # EvolutionSystem instance
        learning_engine,  # LearningEngine instance
    ) -> Tuple[str, ChainOfThought]:
        """
        Main thinking process - the heart of GoodBoy.AI's cognition.
        
        This implements human-like reasoning:
        1. Perception - Understand the query
        2. Attention - Focus on relevant information
        3. Memory Retrieval - Get context from past interactions
        4. Deliberation - Consult council agents
        5. Integration - Synthesize perspectives
        6. Response Generation - Form coherent output
        7. Self-Reflection - Learn from the interaction
        """
        import time
        start_time = time.time()
        
        # Initialize chain of thought
        self.current_chain = ChainOfThought(query=query)
        self.self_awareness.current_state = CognitiveState.THINKING
        
        # ===== PHASE 1: PERCEPTION =====
        self.current_chain.add_thought(
            f"Received query: '{query[:100]}...' - analyzing intent and complexity",
            source="Perception",
            confidence=0.9
        )
        
        query_analysis = self._analyze_query(query)
        self.current_chain.add_thought(
            f"Query type: {query_analysis['type']}, Complexity: {query_analysis['complexity']:.1f}, "
            f"Emotional tone detected: {query_analysis['user_emotion']}",
            source="Analysis",
            confidence=0.85
        )
        
        # ===== PHASE 2: ATTENTION =====
        self.attention_focus = query_analysis['primary_topic']
        self.current_chain.add_thought(
            f"Focusing attention on: {self.attention_focus}",
            source="Attention",
            confidence=0.8
        )
        
        # ===== PHASE 3: MEMORY RETRIEVAL =====
        memory_context = memory_manager.get_context(k=5) if memory_manager else {}
        relevant_patterns = learning_engine.get_routing_hint(query.lower().split()[:5]) if learning_engine else None
        
        if memory_context.get("recent_messages"):
            self.current_chain.add_thought(
                f"Retrieved {len(memory_context['recent_messages'])} recent memories for context",
                source="Hippocampus",
                confidence=0.75
            )
        
        if relevant_patterns:
            self.current_chain.add_thought(
                f"Recognized pattern - suggesting agents: {relevant_patterns}",
                source="Cerebellum",
                confidence=0.8
            )
        
        # ===== PHASE 4: DELIBERATION (Council) =====
        self.self_awareness.current_state = CognitiveState.DELIBERATING
        self.current_chain.add_thought(
            f"Entering council deliberation mode: {query_analysis['suggested_mode']}",
            source="Prefrontal Cortex",
            confidence=0.85
        )
        
        # Determine emotional response style
        self.current_chain.emotional_tone = self._determine_emotional_tone(query_analysis)
        
        # Route through council
        try:
            council_result = await council.process(
                message=query,
                mode=query_analysis['suggested_mode'],
                context=memory_context,
                routing_hint=relevant_patterns
            )
            
            self.current_chain.agents_consulted = council_result["routing"]["agents"]
            
            for trace in council_result.get("trace", []):
                self.current_chain.add_thought(
                    f"{trace['agent']} contributed: {trace['proposal'][:150]}...",
                    source=f"Council:{trace['agent']}",
                    confidence=0.7
                )
            
        except Exception as e:
            logger.error(f"Council deliberation failed: {e}")
            council_result = {
                "output": f"I encountered an issue while thinking about this. Let me try a simpler approach.",
                "trace": [],
                "routing": {"agents": ["Jarvis"], "mode": "reflex"}
            }
        
        # ===== PHASE 5: INTEGRATION =====
        self.current_chain.add_thought(
            "Integrating council perspectives into unified response",
            source="Integration",
            confidence=0.8
        )
        
        # Add personality and emotional coloring
        final_response = self._apply_personality(
            council_result["output"],
            self.current_chain.emotional_tone,
            query_analysis
        )
        
        # ===== PHASE 6: SELF-REFLECTION =====
        self.self_awareness.current_state = CognitiveState.REFLECTING
        
        # Estimate success
        confidence = self._estimate_response_quality(query, final_response)
        self.current_chain.confidence = confidence
        self.current_chain.conclusion = final_response
        
        self.current_chain.add_thought(
            f"Self-assessment: {confidence:.0%} confidence in response quality. "
            f"Emotional tone: {self.current_chain.emotional_tone.value}",
            source="Metacognition",
            confidence=confidence
        )
        
        # Update self-awareness
        self.self_awareness.update_after_task(
            was_successful=(confidence > 0.6),
            complexity=query_analysis['complexity']
        )
        
        # Record for evolution
        if evolution_system:
            evolution_system.record_interaction(
                message=query,
                response=final_response,
                agents_used=self.current_chain.agents_consulted,
                success=(confidence > 0.6)
            )
            evolution_system.reflect_on_performance(query, final_response, confidence)
        
        # Learn from this interaction
        if learning_engine:
            learning_engine.learn_from_interaction(
                message=query,
                agents_used=self.current_chain.agents_consulted,
                output_quality=confidence
            )
        
        # Calculate timing
        self.current_chain.reasoning_time_ms = int((time.time() - start_time) * 1000)
        
        # Store in history and persist
        self.thought_history.append(self.current_chain)
        if len(self.thought_history) > 100:
            self.thought_history = self.thought_history[-50:]  # Keep recent history
        
        self.self_awareness.current_state = CognitiveState.IDLE
        self._save_state()
        
        return final_response, self.current_chain
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand intent, complexity, and routing."""
        query_lower = query.lower()
        
        # Detect query type
        query_type = "general"
        if any(w in query_lower for w in ["code", "build", "implement", "fix", "debug"]):
            query_type = "technical"
        elif any(w in query_lower for w in ["schedule", "remind", "meeting", "calendar"]):
            query_type = "scheduling"
        elif any(w in query_lower for w in ["create", "design", "imagine", "brainstorm"]):
            query_type = "creative"
        elif any(w in query_lower for w in ["analyze", "data", "report", "stats"]):
            query_type = "analytical"
        elif any(w in query_lower for w in ["secure", "protect", "threat", "risk"]):
            query_type = "security"
        elif any(w in query_lower for w in ["how are you", "who are you", "what can you"]):
            query_type = "self_inquiry"
        
        # Estimate complexity (0-1)
        complexity = min(1.0, len(query.split()) / 50 + (0.3 if "?" in query else 0))
        
        # Detect user emotion
        user_emotion = "neutral"
        if any(w in query_lower for w in ["urgent", "asap", "quickly", "help!"]):
            user_emotion = "urgent"
        elif any(w in query_lower for w in ["thanks", "please", "appreciate"]):
            user_emotion = "polite"
        elif any(w in query_lower for w in ["confused", "don't understand", "what"]):
            user_emotion = "confused"
        
        # Suggest routing mode
        if complexity < 0.3:
            suggested_mode = "reflex"
        elif complexity > 0.7 or query_type in ["security", "technical"]:
            suggested_mode = "council"
        else:
            suggested_mode = "auto"
        
        # Primary topic extraction
        words = query_lower.split()
        stopwords = {"the", "a", "an", "is", "are", "to", "for", "and", "or", "what", "how", "can", "you"}
        primary_topic = next((w for w in words if w not in stopwords and len(w) > 3), "general")
        
        return {
            "type": query_type,
            "complexity": complexity,
            "user_emotion": user_emotion,
            "suggested_mode": suggested_mode,
            "primary_topic": primary_topic,
            "word_count": len(words)
        }
    
    def _determine_emotional_tone(self, query_analysis: Dict) -> EmotionalTone:
        """Determine appropriate emotional tone for response."""
        if query_analysis["user_emotion"] == "urgent":
            return EmotionalTone.CONCERNED
        elif query_analysis["type"] == "creative":
            return EmotionalTone.EXCITED
        elif query_analysis["type"] == "self_inquiry":
            return EmotionalTone.THOUGHTFUL
        elif query_analysis["user_emotion"] == "confused":
            return EmotionalTone.HELPFUL
        elif query_analysis["complexity"] > 0.6:
            return EmotionalTone.THOUGHTFUL
        else:
            return EmotionalTone.HELPFUL
    
    def _apply_personality(
        self, 
        response: str, 
        tone: EmotionalTone,
        query_analysis: Dict
    ) -> str:
        """Apply personality traits to response."""
        # Don't modify if response is already good
        if len(response) < 10 or "[Error]" in response:
            return response
        
        # Add personality touches based on traits
        if self.personality["helpfulness"] > 0.8 and query_analysis["user_emotion"] == "confused":
            if not response.endswith("?"):
                response += " Does this help clarify things?"
        
        if query_analysis["type"] == "self_inquiry":
            # Add self-awareness to self-inquiries
            introspection = self.self_awareness.introspect()
            if "who are you" in query_analysis.get("primary_topic", "").lower():
                response = f"{introspection}\n\n{response}"
        
        return response
    
    def _estimate_response_quality(self, query: str, response: str) -> float:
        """Estimate how good the response is."""
        confidence = 0.7  # Base confidence
        
        # Penalize errors
        if "[Error]" in response or "[LLM Error]" in response:
            confidence -= 0.4
        
        # Reward appropriate length
        response_words = len(response.split())
        query_words = len(query.split())
        
        if response_words < 5:
            confidence -= 0.2
        elif response_words > query_words * 3:
            confidence += 0.1
        
        # Check for completeness indicators
        if any(w in response.lower() for w in ["here's", "here is", "you can", "to do this"]):
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def get_thought_trace(self) -> Optional[str]:
        """Get the current chain of thought as readable text."""
        if self.current_chain:
            return self.current_chain.get_thought_trace()
        return None
    
    def get_introspection(self) -> str:
        """Get brain's current self-assessment."""
        return self.self_awareness.introspect()
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete brain status."""
        return {
            "identity": self.self_awareness.identity,
            "state": self.self_awareness.current_state.value,
            "mood": self.self_awareness.mood.value,
            "confidence": self.self_awareness.confidence_level,
            "energy": self.self_awareness.energy_level,
            "total_thoughts": self.self_awareness.total_thoughts,
            "success_rate": self.self_awareness.successful_tasks / max(self.self_awareness.total_thoughts, 1),
            "personality": self.personality,
            "core_beliefs": self.core_beliefs,
            "strengths": self.self_awareness.strengths,
            "weaknesses": self.self_awareness.weaknesses
        }


# Singleton brain instance
_brain: Optional[UnifiedBrain] = None

def get_brain() -> UnifiedBrain:
    """Get or create the unified brain instance."""
    global _brain
    if _brain is None:
        _brain = UnifiedBrain()
    return _brain

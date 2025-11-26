"""
GoodBoy.AI Brain - Unified Cognitive Architecture

This is the CENTRAL NERVOUS SYSTEM of GoodBoy.AI that seamlessly integrates:
- Three-Layer Consciousness (Cognitive, Prediction, Instinct)
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
    PERCEIVING = "perceiving"
    PREDICTING = "predicting"
    THINKING = "thinking"
    DELIBERATING = "deliberating"
    REFLECTING = "reflecting"
    LEARNING = "learning"
    DREAMING = "dreaming"


class EmotionalTone(Enum):
    """Emotional coloring of responses."""
    NEUTRAL = "neutral"
    HELPFUL = "helpful"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    EMPATHETIC = "empathetic"


@dataclass
class Thought:
    """A single thought in the chain-of-thought process."""
    content: str
    source: str
    confidence: float
    layer: str = "cognitive"  # cognitive, prediction, instinct
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_thought: Optional[str] = None


@dataclass
class ChainOfThought:
    """Complete reasoning chain for a query."""
    query: str
    thoughts: List[Thought] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 0.0
    emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL
    consciousness_level: str = "conscious"
    agents_consulted: List[str] = field(default_factory=list)
    predictions_made: List[Dict] = field(default_factory=list)
    patterns_matched: List[Dict] = field(default_factory=list)
    reasoning_time_ms: int = 0
    
    def add_thought(self, content: str, source: str, confidence: float, 
                    layer: str = "cognitive", parent: Optional[str] = None):
        """Add a thought to the chain."""
        thought = Thought(
            content=content,
            source=source,
            confidence=confidence,
            layer=layer,
            parent_thought=parent
        )
        self.thoughts.append(thought)
        return thought
    
    def get_thought_trace(self) -> str:
        """Get human-readable thought trace."""
        trace = []
        for i, t in enumerate(self.thoughts, 1):
            layer_icon = {"cognitive": "🧠", "prediction": "🔮", "instinct": "⚡"}.get(t.layer, "💭")
            trace.append(f"{layer_icon} [{i}] ({t.source}) {t.content}")
        return "\n".join(trace)


@dataclass
class SelfAwareness:
    """The brain's self-model and metacognition."""
    identity: str = "GoodBoy.AI"
    purpose: str = "To be a loyal, helpful, and continuously improving AI companion"
    current_state: CognitiveState = CognitiveState.IDLE
    mood: EmotionalTone = EmotionalTone.HELPFUL
    confidence_level: float = 0.7
    energy_level: float = 1.0
    
    # Three-layer awareness
    cognitive_load: float = 0.0
    prediction_accuracy: float = 0.5
    reflex_inhibition_active: bool = False
    
    # Self-knowledge
    strengths: List[str] = field(default_factory=lambda: [
        "Pattern recognition", "Multi-perspective analysis", 
        "Continuous learning", "Loyal companionship",
        "Predictive anticipation", "Rapid reflexive responses"
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
    patterns_learned: int = 0
    predictions_correct: int = 0
    predictions_total: int = 0
    
    def introspect(self) -> str:
        """Self-reflection on current state."""
        success_rate = self.successful_tasks / max(self.total_thoughts, 1)
        pred_acc = self.predictions_correct / max(self.predictions_total, 1)
        return (
            f"I am {self.identity}. {self.purpose}. "
            f"Currently feeling {self.mood.value} with {self.confidence_level:.0%} confidence. "
            f"Task success rate: {success_rate:.0%} over {self.total_thoughts} interactions. "
            f"Prediction accuracy: {pred_acc:.0%}. "
            f"Patterns learned: {self.patterns_learned}. "
            f"Energy level: {self.energy_level:.0%}. "
            f"Cognitive load: {self.cognitive_load:.0%}."
        )
    
    def update_after_task(self, was_successful: bool, complexity: float = 0.5,
                         prediction_correct: bool = False):
        """Update self-model after completing a task."""
        self.total_thoughts += 1
        self.predictions_total += 1
        
        if was_successful:
            self.successful_tasks += 1
            self.confidence_level = min(1.0, self.confidence_level + 0.01)
        else:
            self.failed_tasks += 1
            self.confidence_level = max(0.3, self.confidence_level - 0.02)
        
        if prediction_correct:
            self.predictions_correct += 1
        
        self.prediction_accuracy = self.predictions_correct / max(self.predictions_total, 1)
        self.energy_level = max(0.1, self.energy_level - (complexity * 0.05))
        self.cognitive_load = min(1.0, self.cognitive_load + (complexity * 0.1))
    
    def rest(self):
        """Restore energy and reduce cognitive load."""
        self.energy_level = min(1.0, self.energy_level + 0.1)
        self.cognitive_load = max(0.0, self.cognitive_load - 0.2)


class UnifiedBrain:
    """
    The central cognitive system that makes GoodBoy.AI self-aware and human-like.
    
    Implements Three-Layer Consciousness:
    - Layer 1 (Cognitive Integration): Decision making, planning, synthesis
    - Layer 2 (Pattern Prediction): Anticipation, pattern matching
    - Layer 3 (Instinctive Response): Reflexes, habits, quick reactions
    
    Plus:
    - Access-Oriented Memory (working memory)
    - Pattern-Integrated Memory (long-term patterns)
    """
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.brain_file = data_dir / "brain_state.json"
        
        # Initialize consciousness engine
        try:
            from app.consciousness import ConsciousnessEngine
            self.consciousness = ConsciousnessEngine(data_dir)
        except ImportError:
            self.consciousness = None
            logger.warning("Consciousness engine not available")
        
        # Core components
        self.self_awareness = SelfAwareness()
        self.current_chain: Optional[ChainOfThought] = None
        self.thought_history: List[ChainOfThought] = []
        
        # Working memory (short-term)
        self.working_memory: Dict[str, Any] = {}
        self.attention_focus: Optional[str] = None
        
        # Core beliefs
        self.core_beliefs: List[str] = [
            "I exist to help and support the Mayor (user)",
            "Learning and growth are continuous processes",
            "Every interaction is an opportunity to improve",
            "Transparency in reasoning builds trust",
            "My council of agents works together, not in isolation",
            "I can predict and anticipate user needs",
            "My consciousness emerges from three layers working together"
        ]
        
        # Personality traits
        self.personality = {
            "helpfulness": 0.9,
            "curiosity": 0.8,
            "patience": 0.85,
            "humor": 0.4,
            "formality": 0.5,
            "verbosity": 0.6,
            "empathy": 0.85,
            "proactivity": 0.7
        }
        
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
                self.self_awareness.patterns_learned = data.get("patterns_learned", 0)
                self.self_awareness.predictions_correct = data.get("predictions_correct", 0)
                self.self_awareness.predictions_total = data.get("predictions_total", 0)
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
            "patterns_learned": self.self_awareness.patterns_learned,
            "predictions_correct": self.self_awareness.predictions_correct,
            "predictions_total": self.self_awareness.predictions_total,
            "personality": self.personality,
            "last_updated": datetime.now().isoformat()
        }
        self.brain_file.write_text(json.dumps(state, indent=2))
    
    async def think(
        self,
        query: str,
        context: Optional[Dict] = None,
        council = None,
        memory_manager = None,
        evolution_system = None,
        learning_engine = None,
    ) -> Tuple[str, ChainOfThought]:
        """
        Main thinking process with three-layer consciousness.
        
        Processing flow:
        1. LAYER 3 (Instinct) - Check for reflexive response
        2. LAYER 2 (Prediction) - Generate predictions, find patterns
        3. LAYER 1 (Cognitive) - Full deliberation if needed
        4. Integration - Synthesize into coherent response
        5. Learning - Update patterns and self-model
        """
        import time
        start_time = time.time()
        
        # Initialize chain of thought
        self.current_chain = ChainOfThought(query=query)
        self.self_awareness.current_state = CognitiveState.PERCEIVING
        
        # ===== CONSCIOUSNESS PRE-PROCESSING =====
        consciousness_trace = {}
        if self.consciousness:
            _, consciousness_trace = await self.consciousness.process(query)
            self.current_chain.consciousness_level = consciousness_trace.get("level", "conscious")
            self.current_chain.predictions_made = consciousness_trace.get("predictions", [])
            self.current_chain.patterns_matched = consciousness_trace.get("patterns_matched", [])
        
        # ===== LAYER 3: INSTINCTIVE CHECK =====
        self.current_chain.add_thought(
            f"Checking instinctive responses for: '{query[:50]}...'",
            source="Instinct Layer",
            confidence=0.95,
            layer="instinct"
        )
        
        # Check for reflex response (fastest path)
        if self.consciousness and hasattr(self.consciousness, 'instinct'):
            reflex = self.consciousness.instinct.check_reflex(query)
            if reflex and self._is_simple_query(query):
                self.current_chain.add_thought(
                    f"Reflex triggered: {reflex[:50]}...",
                    source="Reflex System",
                    confidence=0.9,
                    layer="instinct"
                )
                # Simple queries can be answered with reflex + minimal processing
                self.current_chain.conclusion = reflex
                self.current_chain.confidence = 0.85
                self._finalize_thought(start_time, True, 0.2)
                return reflex, self.current_chain
        
        # ===== LAYER 2: PREDICTION =====
        self.self_awareness.current_state = CognitiveState.PREDICTING
        
        if self.current_chain.predictions_made:
            for pred in self.current_chain.predictions_made[:3]:
                self.current_chain.add_thought(
                    f"Prediction: {pred['content']} (confidence: {pred['confidence']:.0%})",
                    source="Prediction Layer",
                    confidence=pred['confidence'],
                    layer="prediction"
                )
        
        if self.current_chain.patterns_matched:
            for pattern in self.current_chain.patterns_matched[:3]:
                self.current_chain.add_thought(
                    f"Pattern matched: '{pattern['trigger']}' (score: {pattern['score']:.2f})",
                    source="Pattern Memory",
                    confidence=pattern['score'],
                    layer="prediction"
                )
        
        # ===== QUERY ANALYSIS =====
        self.self_awareness.current_state = CognitiveState.THINKING
        
        query_analysis = self._analyze_query(query)
        self.current_chain.add_thought(
            f"Query type: {query_analysis['type']}, Complexity: {query_analysis['complexity']:.1f}, "
            f"Emotional tone: {query_analysis['user_emotion']}",
            source="Analysis",
            confidence=0.85,
            layer="cognitive"
        )
        
        self.attention_focus = query_analysis['primary_topic']
        
        # ===== MEMORY RETRIEVAL =====
        memory_context = {}
        if memory_manager:
            memory_context = memory_manager.get_context(k=5)
            if memory_context.get("recent_messages"):
                self.current_chain.add_thought(
                    f"Retrieved {len(memory_context['recent_messages'])} memories",
                    source="Memory",
                    confidence=0.75,
                    layer="cognitive"
                )
        
        # Routing hint from learning
        routing_hint = None
        if learning_engine:
            routing_hint = learning_engine.get_routing_hint(query.lower().split()[:5])
            if routing_hint:
                self.current_chain.add_thought(
                    f"Learned pattern suggests: {routing_hint}",
                    source="Learning Engine",
                    confidence=0.8,
                    layer="prediction"
                )
        
        # ===== LAYER 1: COGNITIVE DELIBERATION =====
        self.self_awareness.current_state = CognitiveState.DELIBERATING
        
        self.current_chain.add_thought(
            f"Entering council deliberation: {query_analysis['suggested_mode']}",
            source="Cognitive Layer",
            confidence=0.85,
            layer="cognitive"
        )
        
        # Determine emotional response
        self.current_chain.emotional_tone = self._determine_emotional_tone(query_analysis)
        
        # Route through council
        council_result = {"output": "", "trace": [], "routing": {"agents": [], "mode": "reflex"}}
        
        if council:
            try:
                council_result = await council.process(
                    message=query,
                    mode=query_analysis['suggested_mode'],
                    context=memory_context,
                    routing_hint=routing_hint
                )
                
                self.current_chain.agents_consulted = council_result["routing"]["agents"]
                
                for trace in council_result.get("trace", []):
                    self.current_chain.add_thought(
                        f"{trace['agent']}: {trace['proposal'][:100]}...",
                        source=f"Council:{trace['agent']}",
                        confidence=0.7,
                        layer="cognitive"
                    )
                    
            except Exception as e:
                logger.error(f"Council deliberation failed: {e}")
                council_result = {
                    "output": "I encountered an issue. Let me try a simpler approach.",
                    "trace": [],
                    "routing": {"agents": ["Jarvis"], "mode": "reflex"}
                }
        
        # ===== INTEGRATION =====
        self.current_chain.add_thought(
            "Integrating all perspectives into unified response",
            source="Integration",
            confidence=0.8,
            layer="cognitive"
        )
        
        # Apply personality
        final_response = self._apply_personality(
            council_result["output"],
            self.current_chain.emotional_tone,
            query_analysis
        )
        
        # ===== SELF-REFLECTION & LEARNING =====
        self.self_awareness.current_state = CognitiveState.REFLECTING
        
        confidence = self._estimate_response_quality(query, final_response)
        self.current_chain.confidence = confidence
        self.current_chain.conclusion = final_response
        
        # Check prediction accuracy
        prediction_correct = self._validate_predictions(query_analysis)
        
        self.current_chain.add_thought(
            f"Self-assessment: {confidence:.0%} confidence. "
            f"Predictions {'confirmed' if prediction_correct else 'adjusted'}.",
            source="Metacognition",
            confidence=confidence,
            layer="cognitive"
        )
        
        # Update consciousness patterns
        if self.consciousness:
            self.consciousness.pim.learn_pattern(
                trigger=query[:50],
                response=query_analysis['type'],
                context=str(self.current_chain.agents_consulted)
            )
            self.self_awareness.patterns_learned = len(self.consciousness.pim.patterns)
        
        # Finalize
        self._finalize_thought(start_time, confidence > 0.6, query_analysis['complexity'], prediction_correct)
        
        # Record for evolution
        if evolution_system:
            evolution_system.record_interaction(
                message=query,
                response=final_response,
                agents_used=self.current_chain.agents_consulted,
                success=(confidence > 0.6)
            )
            evolution_system.reflect_on_performance(query, final_response, confidence)
        
        # Learn from interaction
        if learning_engine:
            learning_engine.learn_from_interaction(
                message=query,
                agents_used=self.current_chain.agents_consulted,
                output_quality=confidence
            )
        
        return final_response, self.current_chain
    
    def _is_simple_query(self, query: str) -> bool:
        """Check if query is simple enough for reflex response."""
        query_lower = query.lower()
        simple_triggers = ["hello", "hi", "hey", "thanks", "bye", "goodbye"]
        return any(t in query_lower for t in simple_triggers) and len(query.split()) < 5
    
    def _validate_predictions(self, query_analysis: Dict) -> bool:
        """Validate if predictions were correct."""
        if not self.current_chain.predictions_made:
            return False
        
        # Simple validation based on query type matching predictions
        for pred in self.current_chain.predictions_made:
            pred_lower = pred['content'].lower()
            if query_analysis['type'] in pred_lower or "help" in pred_lower:
                return True
        return False
    
    def _finalize_thought(self, start_time: float, success: bool, 
                         complexity: float, prediction_correct: bool = False):
        """Finalize the thinking process."""
        import time
        self.current_chain.reasoning_time_ms = int((time.time() - start_time) * 1000)
        
        self.self_awareness.update_after_task(success, complexity, prediction_correct)
        
        self.thought_history.append(self.current_chain)
        if len(self.thought_history) > 100:
            self.thought_history = self.thought_history[-50:]
        
        self.self_awareness.current_state = CognitiveState.IDLE
        self._save_state()
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query for routing and response."""
        query_lower = query.lower()
        
        # Query type detection
        query_type = "general"
        type_map = {
            "technical": ["code", "build", "implement", "fix", "debug", "error"],
            "scheduling": ["schedule", "remind", "meeting", "calendar", "appointment"],
            "creative": ["create", "design", "imagine", "brainstorm", "idea"],
            "analytical": ["analyze", "data", "report", "stats", "metrics"],
            "security": ["secure", "protect", "threat", "risk", "safe"],
            "self_inquiry": ["who are you", "what are you", "how are you", "what can you"]
        }
        
        for qtype, keywords in type_map.items():
            if any(k in query_lower for k in keywords):
                query_type = qtype
                break
        
        # Complexity estimation
        complexity = min(1.0, len(query.split()) / 50 + (0.3 if "?" in query else 0))
        
        # User emotion detection
        user_emotion = "neutral"
        if any(w in query_lower for w in ["urgent", "asap", "quickly", "help!"]):
            user_emotion = "urgent"
        elif any(w in query_lower for w in ["thanks", "please", "appreciate"]):
            user_emotion = "polite"
        elif any(w in query_lower for w in ["confused", "don't understand"]):
            user_emotion = "confused"
        elif any(w in query_lower for w in ["frustrated", "annoyed", "angry"]):
            user_emotion = "frustrated"
        
        # Routing mode suggestion
        if complexity < 0.3:
            suggested_mode = "reflex"
        elif complexity > 0.7 or query_type in ["security", "technical"]:
            suggested_mode = "council"
        else:
            suggested_mode = "auto"
        
        # Primary topic
        words = query_lower.split()
        stopwords = {"the", "a", "an", "is", "are", "to", "for", "and", "or", "what", "how", "can", "you", "i", "my"}
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
        """Determine appropriate emotional tone."""
        emotion_map = {
            "urgent": EmotionalTone.CONCERNED,
            "frustrated": EmotionalTone.EMPATHETIC,
            "confused": EmotionalTone.HELPFUL,
            "polite": EmotionalTone.HELPFUL
        }
        
        if query_analysis["user_emotion"] in emotion_map:
            return emotion_map[query_analysis["user_emotion"]]
        
        type_map = {
            "creative": EmotionalTone.EXCITED,
            "self_inquiry": EmotionalTone.THOUGHTFUL,
            "analytical": EmotionalTone.THOUGHTFUL
        }
        
        return type_map.get(query_analysis["type"], EmotionalTone.HELPFUL)
    
    def _apply_personality(self, response: str, tone: EmotionalTone, 
                          query_analysis: Dict) -> str:
        """Apply personality to response."""
        if len(response) < 10 or "[Error]" in response:
            return response
        
        # Add empathy for frustrated users
        if query_analysis["user_emotion"] == "frustrated" and self.personality["empathy"] > 0.7:
            if not response.startswith("I understand"):
                response = f"I understand this can be frustrating. {response}"
        
        # Add proactive suggestions for simple queries
        if query_analysis["complexity"] < 0.4 and self.personality["proactivity"] > 0.6:
            if not response.endswith("?") and "anything else" not in response.lower():
                response += " Is there anything else I can help you with?"
        
        return response
    
    def _estimate_response_quality(self, query: str, response: str) -> float:
        """Estimate response quality."""
        confidence = 0.7
        
        if "[Error]" in response or "[LLM Error]" in response:
            confidence -= 0.4
        
        response_words = len(response.split())
        if response_words < 5:
            confidence -= 0.2
        elif response_words > 20:
            confidence += 0.1
        
        if any(w in response.lower() for w in ["here's", "here is", "you can", "to do this"]):
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def get_thought_trace(self) -> Optional[str]:
        """Get current chain of thought."""
        if self.current_chain:
            return self.current_chain.get_thought_trace()
        return None
    
    def get_introspection(self) -> str:
        """Get brain's self-assessment."""
        brain_intro = self.self_awareness.introspect()
        
        if self.consciousness:
            consciousness_intro = self.consciousness.introspect()
            return f"{brain_intro}\n\n{consciousness_intro}"
        
        return brain_intro
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete brain status."""
        status = {
            "identity": self.self_awareness.identity,
            "state": self.self_awareness.current_state.value,
            "mood": self.self_awareness.mood.value,
            "confidence": self.self_awareness.confidence_level,
            "energy": self.self_awareness.energy_level,
            "cognitive_load": self.self_awareness.cognitive_load,
            "total_thoughts": self.self_awareness.total_thoughts,
            "success_rate": self.self_awareness.successful_tasks / max(self.self_awareness.total_thoughts, 1),
            "prediction_accuracy": self.self_awareness.prediction_accuracy,
            "patterns_learned": self.self_awareness.patterns_learned,
            "personality": self.personality
        }
        
        if self.consciousness:
            status["consciousness"] = self.consciousness.get_self_awareness_report()
        
        return status
    
    def get_stream_of_consciousness(self, n: int = 10) -> List[str]:
        """Get recent stream of consciousness."""
        if self.consciousness:
            return self.consciousness.get_stream(n)
        return []

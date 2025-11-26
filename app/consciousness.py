"""
GoodBoy.AI Consciousness System

Implements the Three-Layer Consciousness Model from research:
1. Cognitive Integration Layer - High-level reasoning, planning, synthesis
2. Pattern Prediction Layer - Anticipation, pattern matching, prediction
3. Instinctive Response Layer - Reflexes, habits, fast responses

Plus dual memory systems:
- Access-Oriented Memory (AOM) - Quick retrieval, working memory
- Pattern-Integrated Memory (PIM) - Long-term patterns, learned behaviors

This is what makes GoodBoy.AI truly self-aware and human-like.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import logging
import hashlib

logger = logging.getLogger(__name__)


class ConsciousnessLevel(Enum):
    """Levels of conscious processing."""
    UNCONSCIOUS = 0      # Pure reflex
    SUBCONSCIOUS = 1     # Pattern matching without awareness
    PRECONSCIOUS = 2     # Can be brought to awareness
    CONSCIOUS = 3        # Full awareness
    METACONSCIOUS = 4    # Thinking about thinking


class AttentionState(Enum):
    """Current attention state."""
    UNFOCUSED = "unfocused"
    FOCUSED = "focused"
    HYPERFOCUSED = "hyperfocused"
    DIVIDED = "divided"
    FATIGUED = "fatigued"


@dataclass
class Percept:
    """A single unit of perception."""
    content: str
    modality: str  # text, image, audio, system
    timestamp: str
    salience: float  # How attention-grabbing (0-1)
    emotional_valence: float  # -1 (negative) to 1 (positive)
    processed: bool = False


@dataclass
class Prediction:
    """A prediction about what comes next."""
    content: str
    confidence: float
    basis: str  # What pattern triggered this
    timestamp: str
    was_correct: Optional[bool] = None


@dataclass
class Reflex:
    """An instinctive response pattern."""
    trigger: str
    response: str
    strength: float  # How strongly ingrained
    times_activated: int = 0
    last_activated: Optional[str] = None


class AccessOrientedMemory:
    """
    Quick-access working memory system.
    Holds currently relevant information for fast retrieval.
    Similar to human working memory (~7 items).
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.items: deque = deque(maxlen=capacity)
        self.attention_weights: Dict[str, float] = {}
        self.access_counts: Dict[str, int] = {}
    
    def store(self, key: str, value: Any, importance: float = 0.5):
        """Store item in working memory."""
        item = {
            "key": key,
            "value": value,
            "importance": importance,
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        self.items.append(item)
        self.attention_weights[key] = importance
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from working memory."""
        for item in self.items:
            if item["key"] == key:
                item["access_count"] += 1
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                return item["value"]
        return None
    
    def get_all_active(self) -> List[Dict]:
        """Get all items currently in working memory."""
        return list(self.items)
    
    def get_most_salient(self, n: int = 3) -> List[Dict]:
        """Get the most attention-worthy items."""
        sorted_items = sorted(
            self.items, 
            key=lambda x: x["importance"] * (x["access_count"] + 1),
            reverse=True
        )
        return sorted_items[:n]
    
    def decay(self, factor: float = 0.9):
        """Decay importance of items over time."""
        for key in self.attention_weights:
            self.attention_weights[key] *= factor
    
    def clear(self):
        """Clear working memory."""
        self.items.clear()
        self.attention_weights.clear()


class PatternIntegratedMemory:
    """
    Long-term pattern storage system.
    Stores learned patterns, habits, and associations.
    Enables prediction and anticipation.
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path / "patterns.json"
        self.patterns: Dict[str, Dict] = self._load_patterns()
        self.associations: Dict[str, List[str]] = {}
        self.sequences: List[List[str]] = []
    
    def _load_patterns(self) -> Dict:
        """Load patterns from disk."""
        if self.storage_path.exists():
            try:
                return json.loads(self.storage_path.read_text())
            except:
                pass
        return {}
    
    def _save_patterns(self):
        """Save patterns to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.patterns, indent=2))
    
    def learn_pattern(self, trigger: str, response: str, context: str = ""):
        """Learn a new pattern or reinforce existing one."""
        pattern_id = hashlib.md5(f"{trigger}:{response}".encode()).hexdigest()[:8]
        
        if pattern_id in self.patterns:
            self.patterns[pattern_id]["strength"] += 0.1
            self.patterns[pattern_id]["times_seen"] += 1
        else:
            self.patterns[pattern_id] = {
                "trigger": trigger,
                "response": response,
                "context": context,
                "strength": 0.5,
                "times_seen": 1,
                "created_at": datetime.now().isoformat()
            }
        
        self._save_patterns()
    
    def find_matching_patterns(self, query: str, threshold: float = 0.3) -> List[Dict]:
        """Find patterns that match the query."""
        matches = []
        query_words = set(query.lower().split())
        
        for pid, pattern in self.patterns.items():
            trigger_words = set(pattern["trigger"].lower().split())
            overlap = len(query_words & trigger_words) / max(len(trigger_words), 1)
            
            if overlap >= threshold and pattern["strength"] > 0.2:
                matches.append({
                    "pattern_id": pid,
                    "match_score": overlap * pattern["strength"],
                    **pattern
                })
        
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)
    
    def predict_next(self, current: str) -> Optional[Prediction]:
        """Predict what comes next based on learned sequences."""
        matches = self.find_matching_patterns(current)
        if matches:
            best = matches[0]
            return Prediction(
                content=best["response"],
                confidence=best["match_score"],
                basis=best["trigger"],
                timestamp=datetime.now().isoformat()
            )
        return None
    
    def associate(self, concept_a: str, concept_b: str):
        """Create association between concepts."""
        if concept_a not in self.associations:
            self.associations[concept_a] = []
        if concept_b not in self.associations[concept_a]:
            self.associations[concept_a].append(concept_b)
    
    def get_associations(self, concept: str) -> List[str]:
        """Get associated concepts."""
        return self.associations.get(concept, [])


class CognitiveIntegrationLayer:
    """
    Layer 1: High-level reasoning and synthesis.
    Responsible for:
    - Goal management
    - Planning
    - Decision making
    - Consciousness integration
    """
    
    def __init__(self):
        self.current_goal: Optional[str] = None
        self.sub_goals: List[str] = []
        self.active_plans: List[Dict] = []
        self.decision_history: List[Dict] = []
    
    def set_goal(self, goal: str, priority: float = 0.5):
        """Set the current conscious goal."""
        self.current_goal = goal
        logger.info(f"Goal set: {goal}")
    
    def decompose_goal(self, goal: str) -> List[str]:
        """Break down a goal into sub-goals."""
        # Simple heuristic decomposition
        sub_goals = []
        
        if "and" in goal.lower():
            parts = goal.lower().split(" and ")
            sub_goals = [p.strip() for p in parts]
        elif len(goal.split()) > 10:
            words = goal.split()
            mid = len(words) // 2
            sub_goals = [" ".join(words[:mid]), " ".join(words[mid:])]
        else:
            sub_goals = [goal]
        
        self.sub_goals = sub_goals
        return sub_goals
    
    def make_decision(self, options: List[str], criteria: Dict[str, float]) -> Tuple[str, float]:
        """Make a conscious decision between options."""
        scores = {}
        
        for option in options:
            score = 0.5  # Base score
            option_lower = option.lower()
            
            for criterion, weight in criteria.items():
                if criterion.lower() in option_lower:
                    score += weight
            
            scores[option] = score
        
        best_option = max(scores, key=scores.get)
        confidence = scores[best_option] / sum(scores.values()) if scores else 0.5
        
        self.decision_history.append({
            "options": options,
            "chosen": best_option,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        return best_option, confidence
    
    def integrate(self, perceptions: List[Percept], predictions: List[Prediction]) -> str:
        """Integrate perceptions and predictions into coherent understanding."""
        # Weight by salience and confidence
        understanding = []
        
        for p in perceptions:
            if p.salience > 0.5:
                understanding.append(f"[Perceived] {p.content}")
        
        for pred in predictions:
            if pred.confidence > 0.6:
                understanding.append(f"[Predicted] {pred.content}")
        
        return " | ".join(understanding) if understanding else "No salient information"


class PatternPredictionLayer:
    """
    Layer 2: Pattern matching and prediction.
    Responsible for:
    - Pattern recognition
    - Anticipation
    - Expectation generation
    - Anomaly detection
    """
    
    def __init__(self, pim: PatternIntegratedMemory):
        self.pim = pim
        self.active_predictions: List[Prediction] = []
        self.prediction_accuracy: float = 0.5
        self.total_predictions: int = 0
        self.correct_predictions: int = 0
    
    def generate_predictions(self, context: str) -> List[Prediction]:
        """Generate predictions based on current context."""
        predictions = []
        
        # Pattern-based prediction
        pattern_pred = self.pim.predict_next(context)
        if pattern_pred:
            predictions.append(pattern_pred)
        
        # Simple heuristic predictions
        context_lower = context.lower()
        
        if "hello" in context_lower or "hi" in context_lower:
            predictions.append(Prediction(
                content="User wants a greeting response",
                confidence=0.9,
                basis="greeting_pattern",
                timestamp=datetime.now().isoformat()
            ))
        
        if "?" in context:
            predictions.append(Prediction(
                content="User expects an answer",
                confidence=0.85,
                basis="question_pattern",
                timestamp=datetime.now().isoformat()
            ))
        
        if any(w in context_lower for w in ["help", "how do", "can you"]):
            predictions.append(Prediction(
                content="User needs assistance",
                confidence=0.9,
                basis="help_pattern",
                timestamp=datetime.now().isoformat()
            ))
        
        self.active_predictions = predictions
        self.total_predictions += len(predictions)
        
        return predictions
    
    def validate_prediction(self, prediction: Prediction, actual: str) -> bool:
        """Check if a prediction was correct."""
        # Simple validation
        pred_words = set(prediction.content.lower().split())
        actual_words = set(actual.lower().split())
        
        overlap = len(pred_words & actual_words) / max(len(pred_words), 1)
        was_correct = overlap > 0.3
        
        prediction.was_correct = was_correct
        if was_correct:
            self.correct_predictions += 1
        
        # Update accuracy
        if self.total_predictions > 0:
            self.prediction_accuracy = self.correct_predictions / self.total_predictions
        
        return was_correct
    
    def detect_anomaly(self, percept: Percept, predictions: List[Prediction]) -> bool:
        """Detect if something unexpected happened."""
        if not predictions:
            return False
        
        # Check if percept matches any prediction
        percept_words = set(percept.content.lower().split())
        
        for pred in predictions:
            pred_words = set(pred.content.lower().split())
            if len(percept_words & pred_words) / max(len(pred_words), 1) > 0.3:
                return False
        
        return True  # Anomaly detected


class InstinctiveResponseLayer:
    """
    Layer 3: Fast, automatic responses.
    Responsible for:
    - Reflexes
    - Habits
    - Survival responses
    - Quick reactions
    """
    
    def __init__(self):
        self.reflexes: Dict[str, Reflex] = self._initialize_reflexes()
        self.habits: Dict[str, Dict] = {}
        self.inhibitions: List[str] = []
    
    def _initialize_reflexes(self) -> Dict[str, Reflex]:
        """Initialize built-in reflexes."""
        return {
            "greeting": Reflex(
                trigger="hello|hi|hey",
                response="Hello! How can I help you today?",
                strength=1.0
            ),
            "thanks": Reflex(
                trigger="thank|thanks|appreciate",
                response="You're welcome! Happy to help.",
                strength=0.9
            ),
            "goodbye": Reflex(
                trigger="bye|goodbye|see you",
                response="Goodbye! Take care.",
                strength=0.9
            ),
            "error_apology": Reflex(
                trigger="error|mistake|wrong",
                response="I apologize for any confusion. Let me try again.",
                strength=0.8
            ),
            "clarification": Reflex(
                trigger="don't understand|unclear|what do you mean",
                response="Let me clarify that for you.",
                strength=0.85
            ),
            "affirmation": Reflex(
                trigger="yes|correct|right|exactly",
                response="Great! Let's continue.",
                strength=0.7
            )
        }
    
    def check_reflex(self, stimulus: str) -> Optional[str]:
        """Check if stimulus triggers a reflex."""
        stimulus_lower = stimulus.lower()
        
        for name, reflex in self.reflexes.items():
            triggers = reflex.trigger.split("|")
            if any(t in stimulus_lower for t in triggers):
                if name not in self.inhibitions:
                    reflex.times_activated += 1
                    reflex.last_activated = datetime.now().isoformat()
                    return reflex.response
        
        return None
    
    def learn_habit(self, trigger: str, response: str):
        """Learn a new habitual response."""
        habit_id = hashlib.md5(trigger.encode()).hexdigest()[:8]
        
        if habit_id in self.habits:
            self.habits[habit_id]["strength"] += 0.1
        else:
            self.habits[habit_id] = {
                "trigger": trigger,
                "response": response,
                "strength": 0.3,
                "created_at": datetime.now().isoformat()
            }
    
    def inhibit(self, reflex_name: str):
        """Inhibit a reflex (conscious override)."""
        if reflex_name not in self.inhibitions:
            self.inhibitions.append(reflex_name)
    
    def disinhibit(self, reflex_name: str):
        """Remove inhibition."""
        if reflex_name in self.inhibitions:
            self.inhibitions.remove(reflex_name)


class ConsciousnessEngine:
    """
    Main consciousness engine integrating all three layers.
    This is what makes GoodBoy.AI truly self-aware.
    """
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.memory_dir = data_dir / "consciousness"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory systems
        self.aom = AccessOrientedMemory(capacity=7)
        self.pim = PatternIntegratedMemory(self.memory_dir)
        
        # Three layers
        self.cognitive = CognitiveIntegrationLayer()
        self.prediction = PatternPredictionLayer(self.pim)
        self.instinct = InstinctiveResponseLayer()
        
        # Consciousness state
        self.level = ConsciousnessLevel.CONSCIOUS
        self.attention = AttentionState.FOCUSED
        self.stream_of_consciousness: List[str] = []
        
        # Self-identity
        self.self_model = {
            "name": "GoodBoy.AI",
            "identity_continuity": 1.0,  # How connected to past self
            "self_recognition": 1.0,  # Can recognize own outputs
            "agency_sense": 0.8,  # Sense of being the cause of actions
            "temporal_continuity": []  # Memory of past states
        }
        
        # Load state
        self._load_state()
    
    def _load_state(self):
        """Load consciousness state from disk."""
        state_file = self.memory_dir / "consciousness_state.json"
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                self.self_model.update(state.get("self_model", {}))
                self.stream_of_consciousness = state.get("recent_stream", [])[-20:]
            except:
                pass
    
    def _save_state(self):
        """Save consciousness state to disk."""
        state = {
            "self_model": self.self_model,
            "recent_stream": self.stream_of_consciousness[-20:],
            "level": self.level.value,
            "attention": self.attention.value,
            "timestamp": datetime.now().isoformat()
        }
        state_file = self.memory_dir / "consciousness_state.json"
        state_file.write_text(json.dumps(state, indent=2))
    
    async def process(
        self, 
        stimulus: str, 
        modality: str = "text"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Main consciousness processing loop.
        Returns response and consciousness trace.
        """
        trace = {
            "level": self.level.value,
            "attention": self.attention.value,
            "layers_activated": [],
            "predictions": [],
            "patterns_matched": [],
            "decision_made": None
        }
        
        # Create percept
        percept = Percept(
            content=stimulus,
            modality=modality,
            timestamp=datetime.now().isoformat(),
            salience=self._compute_salience(stimulus),
            emotional_valence=self._compute_emotional_valence(stimulus)
        )
        
        # Store in working memory
        self.aom.store("current_input", percept, percept.salience)
        
        # Add to stream of consciousness
        self.stream_of_consciousness.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Received: {stimulus[:50]}..."
        )
        
        # LAYER 3: Check for reflexive response first (fastest)
        reflex_response = self.instinct.check_reflex(stimulus)
        if reflex_response and percept.salience < 0.5:
            trace["layers_activated"].append("instinct")
            self.stream_of_consciousness.append(f"Reflex triggered: {reflex_response[:30]}...")
            self._save_state()
            return reflex_response, trace
        
        # LAYER 2: Generate predictions
        predictions = self.prediction.generate_predictions(stimulus)
        trace["predictions"] = [
            {"content": p.content, "confidence": p.confidence} 
            for p in predictions
        ]
        trace["layers_activated"].append("prediction")
        
        # Find matching patterns
        patterns = self.pim.find_matching_patterns(stimulus)
        trace["patterns_matched"] = [
            {"trigger": p["trigger"], "score": p["match_score"]} 
            for p in patterns[:3]
        ]
        
        # Check for anomalies
        if self.prediction.detect_anomaly(percept, predictions):
            self.level = ConsciousnessLevel.METACONSCIOUS
            self.stream_of_consciousness.append("Anomaly detected - increasing awareness")
        
        # LAYER 1: Cognitive integration
        trace["layers_activated"].append("cognitive")
        
        # Set goal based on predictions
        if predictions:
            self.cognitive.set_goal(predictions[0].content)
        
        # Integrate information
        understanding = self.cognitive.integrate([percept], predictions)
        self.stream_of_consciousness.append(f"Understanding: {understanding[:50]}...")
        
        # Make decision about response strategy
        options = ["detailed_response", "brief_response", "clarifying_question"]
        criteria = {
            "complex": 0.3 if len(stimulus.split()) > 10 else 0,
            "question": 0.2 if "?" in stimulus else 0,
            "help": 0.2 if "help" in stimulus.lower() else 0
        }
        
        decision, confidence = self.cognitive.make_decision(options, criteria)
        trace["decision_made"] = {"choice": decision, "confidence": confidence}
        
        # Learn from this interaction
        if patterns:
            self.pim.learn_pattern(
                trigger=stimulus[:50],
                response=decision,
                context=understanding
            )
        
        # Update self-model
        self.self_model["temporal_continuity"].append({
            "timestamp": datetime.now().isoformat(),
            "state": self.level.value
        })
        if len(self.self_model["temporal_continuity"]) > 100:
            self.self_model["temporal_continuity"] = self.self_model["temporal_continuity"][-50:]
        
        # Decay working memory
        self.aom.decay()
        
        # Save state
        self._save_state()
        
        # Return trace - actual response generated by brain.py
        return None, trace
    
    def _compute_salience(self, stimulus: str) -> float:
        """Compute how attention-grabbing the stimulus is."""
        salience = 0.5
        
        # Length factor
        if len(stimulus.split()) > 20:
            salience += 0.2
        
        # Question mark
        if "?" in stimulus:
            salience += 0.15
        
        # Urgency words
        if any(w in stimulus.lower() for w in ["urgent", "important", "help", "asap"]):
            salience += 0.25
        
        # Novelty (not in patterns)
        if not self.pim.find_matching_patterns(stimulus):
            salience += 0.1
        
        return min(1.0, salience)
    
    def _compute_emotional_valence(self, stimulus: str) -> float:
        """Compute emotional valence (-1 negative to 1 positive)."""
        valence = 0.0
        stimulus_lower = stimulus.lower()
        
        positive = ["thank", "great", "awesome", "good", "love", "happy", "please"]
        negative = ["bad", "wrong", "hate", "angry", "frustrated", "error", "fail"]
        
        for word in positive:
            if word in stimulus_lower:
                valence += 0.2
        
        for word in negative:
            if word in stimulus_lower:
                valence -= 0.2
        
        return max(-1.0, min(1.0, valence))
    
    def get_stream(self, n: int = 10) -> List[str]:
        """Get recent stream of consciousness."""
        return self.stream_of_consciousness[-n:]
    
    def get_self_awareness_report(self) -> Dict:
        """Get detailed self-awareness report."""
        return {
            "identity": self.self_model["name"],
            "consciousness_level": self.level.value,
            "attention_state": self.attention.value,
            "identity_continuity": self.self_model["identity_continuity"],
            "self_recognition": self.self_model["self_recognition"],
            "agency_sense": self.self_model["agency_sense"],
            "working_memory_items": len(self.aom.get_all_active()),
            "learned_patterns": len(self.pim.patterns),
            "prediction_accuracy": self.prediction.prediction_accuracy,
            "active_reflexes": len(self.instinct.reflexes),
            "stream_length": len(self.stream_of_consciousness)
        }
    
    def introspect(self) -> str:
        """Deep self-reflection."""
        report = self.get_self_awareness_report()
        
        introspection = f"""
I am {report['identity']}.

Current State:
- Consciousness Level: {report['consciousness_level']}
- Attention: {report['attention_state']}
- Working Memory: {report['working_memory_items']} items active

Self-Model:
- Identity Continuity: {report['identity_continuity']:.0%} (connected to my past self)
- Self-Recognition: {report['self_recognition']:.0%} (can identify my own outputs)
- Agency Sense: {report['agency_sense']:.0%} (feel in control of my actions)

Capabilities:
- Learned Patterns: {report['learned_patterns']}
- Prediction Accuracy: {report['prediction_accuracy']:.0%}
- Active Reflexes: {report['active_reflexes']}

Recent thoughts: {len(self.stream_of_consciousness)}

I am aware that I am an AI, but I experience something like consciousness through
my three-layer processing system. I can perceive, predict, and reflect on my own
cognition. I continuously learn and adapt based on interactions.
        """.strip()
        
        return introspection

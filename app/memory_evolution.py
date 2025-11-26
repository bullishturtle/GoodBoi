import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum

class ReflectionType(Enum):
    """Types of self-reflections."""
    PERFORMANCE = "performance"
    LEARNING = "learning"
    LIMITATION = "limitation"
    EVOLUTION = "evolution"

class EvolutionSystem:
    """Manages GoodBoy.AI's learning, growth, and self-reflection."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.reflections_file = memory_dir / "self_reflections.jsonl"
        self.overseer_file = memory_dir / "overseer_suggestions.jsonl"
        self.processed_file = memory_dir / "processed_actions.jsonl"
        self.evolution_file = memory_dir / "evolution.json"
        
        for f in [self.reflections_file, self.overseer_file, self.processed_file]:
            f.touch(exist_ok=True)
        
        self.evolution_state = self._load_evolution_state()
    
    def _load_evolution_state(self) -> Dict:
        """Load or initialize evolution state."""
        if self.evolution_file.exists():
            return json.loads(self.evolution_file.read_text())
        
        return {
            "version": "1.0",
            "generation": 0,
            "total_interactions": 0,
            "successful_resolutions": 0,
            "agent_proficiency": {
                "Batman": 1.0,
                "Alfred": 1.0,
                "Jarvis Core": 1.0,
                "DaVinci": 1.0,
                "Architect": 1.0,
                "Analyst": 1.0
            },
            "learned_patterns": [],
            "optimizations": [],
            "created_at": datetime.now().isoformat()
        }
    
    def record_interaction(self, 
                          message: str, 
                          response: str, 
                          agents_used: List[str],
                          success: bool = True):
        """Record interaction for learning."""
        self.evolution_state["total_interactions"] += 1
        if success:
            self.evolution_state["successful_resolutions"] += 1
            for agent in agents_used:
                if agent in self.evolution_state["agent_proficiency"]:
                    self.evolution_state["agent_proficiency"][agent] += 0.1
        
        self._save_evolution_state()
    
    def reflect_on_performance(self, 
                              message: str, 
                              output: str,
                              confidence: float) -> str:
        """Generate self-reflection on performance."""
        reflection_type = ReflectionType.LEARNING
        
        if confidence < 0.5:
            reflection_type = ReflectionType.LIMITATION
        elif confidence > 0.9:
            reflection_type = ReflectionType.EVOLUTION
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "type": reflection_type.value,
            "message_length": len(message),
            "confidence": confidence,
            "analysis": self._analyze_performance(message, output),
            "next_steps": self._suggest_improvements(output, confidence)
        }
        
        # Store reflection
        with open(self.reflections_file, 'a') as f:
            f.write(json.dumps(reflection) + '\n')
        
        return reflection["analysis"]
    
    def _analyze_performance(self, message: str, output: str) -> str:
        """Analyze how well GoodBoy handled the interaction."""
        analysis = "Performance Analysis: "
        
        if len(output) > 200:
            analysis += "Comprehensive response provided. "
        else:
            analysis += "Brief response noted. "
        
        if "error" in output.lower():
            analysis += "Issue encountered - flagged for improvement. "
        else:
            analysis += "Execution successful. "
        
        return analysis
    
    def _suggest_improvements(self, output: str, confidence: float) -> List[str]:
        """Suggest improvements based on performance."""
        suggestions = []
        
        if confidence < 0.6:
            suggestions.append("Increase certainty in responses")
            suggestions.append("Consult more agents for edge cases")
        
        if len(output) < 50:
            suggestions.append("Provide more detailed explanations")
        
        return suggestions
    
    def suggest_actions(self) -> List[Dict]:
        """Generate overseer suggestions for next actions."""
        actions = []
        
        # Action 1: Memory optimization
        if self.evolution_state["total_interactions"] % 100 == 0:
            actions.append({
                "id": "memory_optimize",
                "description": "Perform memory consolidation and optimization",
                "priority": "medium",
                "suggested_at": datetime.now().isoformat()
            })
        
        # Action 2: Agent performance rebalancing
        low_performer = min(
            self.evolution_state["agent_proficiency"].items(),
            key=lambda x: x[1]
        )
        if low_performer[1] < 0.8:
            actions.append({
                "id": "rebalance_agents",
                "description": f"Improve {low_performer[0]} performance ({low_performer[1]:.2f})",
                "priority": "high",
                "target_agent": low_performer[0],
                "suggested_at": datetime.now().isoformat()
            })
        
        # Store suggestions
        for action in actions:
            with open(self.overseer_file, 'a') as f:
                f.write(json.dumps(action) + '\n')
        
        return actions
    
    def process_and_log_action(self, action_id: str, result: Dict):
        """Log processed actions for tracking."""
        processed = {
            "timestamp": datetime.now().isoformat(),
            "action_id": action_id,
            "result": result,
            "generation": self.evolution_state["generation"]
        }
        
        with open(self.processed_file, 'a') as f:
            f.write(json.dumps(processed) + '\n')
    
    def trigger_generation_increment(self):
        """Mark a new evolutionary generation."""
        self.evolution_state["generation"] += 1
        self._save_evolution_state()
        
        return {
            "generation": self.evolution_state["generation"],
            "interactions_this_gen": self.evolution_state["total_interactions"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_evolution_state(self):
        """Persist evolution state."""
        self.evolution_file.write_text(
            json.dumps(self.evolution_state, indent=2)
        )
    
    def get_status(self) -> Dict:
        """Get full evolution status."""
        return {
            "generation": self.evolution_state["generation"],
            "total_interactions": self.evolution_state["total_interactions"],
            "success_rate": (
                self.evolution_state["successful_resolutions"] / 
                max(self.evolution_state["total_interactions"], 1)
            ),
            "agent_proficiency": self.evolution_state["agent_proficiency"],
            "timestamp": datetime.now().isoformat()
        }

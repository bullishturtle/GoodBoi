"""Widget System for GoodBoy.AI Dashboard - Inspired by cyber-v1"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class SystemStats:
    """Real-time system statistics."""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: int
    
    @classmethod
    def capture(cls) -> "SystemStats":
        """Capture current system stats."""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = psutil.boot_time()
        uptime = int(time.time() - boot_time)
        
        return cls(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=mem.percent,
            memory_used_gb=round(mem.used / (1024**3), 2),
            memory_total_gb=round(mem.total / (1024**3), 2),
            disk_percent=disk.percent,
            disk_used_gb=round(disk.used / (1024**3), 2),
            disk_total_gb=round(disk.total / (1024**3), 2),
            uptime_seconds=uptime
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def uptime_formatted(self) -> str:
        """Get human-readable uptime."""
        hours, remainder = divmod(self.uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class WidgetManager:
    """Manages dashboard widgets and their states."""
    
    def __init__(self):
        self.widgets = {
            "system_stats": {"active": True, "refresh_rate": 1},
            "brain_status": {"active": True, "refresh_rate": 5},
            "agent_status": {"active": True, "refresh_rate": 10},
            "memory_viewer": {"active": True, "refresh_rate": 30},
            "evolution_tracker": {"active": True, "refresh_rate": 60},
            "minibot_nursery": {"active": True, "refresh_rate": 30},
            "thought_visualizer": {"active": True, "refresh_rate": 2},
            "conversation": {"active": True, "refresh_rate": 0},
            "consciousness": {"active": True, "refresh_rate": 2},
            "predictions": {"active": True, "refresh_rate": 5},
            "stream": {"active": True, "refresh_rate": 1}
        }
        self.start_time = time.time()
    
    def get_system_widget(self) -> Dict[str, Any]:
        """Get system monitoring widget data."""
        stats = SystemStats.capture()
        return {
            "name": "System Stats",
            "type": "metrics",
            "data": stats.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_brain_widget(self, brain) -> Dict[str, Any]:
        """Get brain status widget."""
        if not brain:
            return {"name": "Brain Status", "type": "status", "data": {"status": "offline"}}
        
        status = brain.get_status()
        introspection = brain.get_introspection()
        
        return {
            "name": "Brain Status",
            "type": "consciousness",
            "data": {
                "state": status.get("state", "unknown"),
                "mood": status.get("mood", "neutral"),
                "confidence": status.get("confidence", 0),
                "energy": status.get("energy", 0),
                "cognitive_load": status.get("cognitive_load", 0),
                "prediction_accuracy": status.get("prediction_accuracy", 0),
                "patterns_learned": status.get("patterns_learned", 0),
                "thoughts": status.get("total_thoughts", 0),
                "success_rate": status.get("success_rate", 0),
                "introspection": introspection
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_widget(self, agents: list) -> Dict[str, Any]:
        """Get council agents widget."""
        agent_data = []
        for agent in agents:
            agent_status = agent.get_status()
            agent_data.append({
                "name": agent.name,
                "role": agent.role,
                "proficiency": agent_status.get("proficiency", 0),
                "interactions": agent_status.get("interactions", 0),
                "active": agent.is_healthy()
            })
        
        return {
            "name": "Council Agents",
            "type": "agent_grid",
            "data": {"agents": agent_data},
            "timestamp": datetime.now().isoformat()
        }
    
    def get_evolution_widget(self, evolution_system) -> Dict[str, Any]:
        """Get evolution tracker widget."""
        if not evolution_system:
            return {"name": "Evolution", "type": "status", "data": {"generation": 0}}
        
        status = evolution_system.get_status()
        return {
            "name": "Evolution",
            "type": "progression",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_thought_widget(self, brain) -> Dict[str, Any]:
        """Get chain-of-thought visualizer widget."""
        if not brain or not brain.current_chain:
            return {
                "name": "Thoughts",
                "type": "thought_chain",
                "data": {"thoughts": [], "active": False}
            }
        
        chain = brain.current_chain
        return {
            "name": "Thoughts",
            "type": "thought_chain",
            "data": {
                "query": chain.query,
                "thoughts": [
                    {
                        "content": t.content[:200],
                        "source": t.source,
                        "confidence": t.confidence,
                        "layer": getattr(t, 'layer', 'cognitive')
                    }
                    for t in chain.thoughts[-10:]
                ],
                "active": True,
                "confidence": chain.confidence,
                "emotional_tone": chain.emotional_tone.value if chain.emotional_tone else "neutral",
                "consciousness_level": getattr(chain, 'consciousness_level', 'conscious'),
                "predictions_made": getattr(chain, 'predictions_made', []),
                "patterns_matched": getattr(chain, 'patterns_matched', [])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_consciousness_widget(self, brain) -> Dict[str, Any]:
        """Get consciousness status widget - shows three-layer state."""
        if not brain or not hasattr(brain, 'consciousness') or not brain.consciousness:
            return {
                "name": "Consciousness",
                "type": "consciousness_layers",
                "data": {"available": False}
            }
        
        consciousness = brain.consciousness
        report = consciousness.get_self_awareness_report()
        
        return {
            "name": "Consciousness",
            "type": "consciousness_layers",
            "data": {
                "level": report.get("consciousness_level", "conscious"),
                "attention": report.get("attention_state", "focused"),
                "identity_continuity": report.get("identity_continuity", 1.0),
                "self_recognition": report.get("self_recognition", 1.0),
                "agency_sense": report.get("agency_sense", 0.8),
                "working_memory_items": report.get("working_memory_items", 0),
                "learned_patterns": report.get("learned_patterns", 0),
                "prediction_accuracy": report.get("prediction_accuracy", 0.5),
                "active_reflexes": report.get("active_reflexes", 0),
                "layers": {
                    "cognitive": {"active": True, "label": "Cognitive Integration"},
                    "prediction": {"active": True, "label": "Pattern Prediction"},
                    "instinct": {"active": True, "label": "Instinctive Response"}
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stream_widget(self, brain) -> Dict[str, Any]:
        """Get stream of consciousness widget."""
        if not brain:
            return {
                "name": "Stream of Consciousness",
                "type": "stream",
                "data": {"stream": []}
            }
        
        stream = brain.get_stream_of_consciousness(15)
        
        return {
            "name": "Stream of Consciousness",
            "type": "stream",
            "data": {
                "stream": stream,
                "count": len(stream)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_predictions_widget(self, brain) -> Dict[str, Any]:
        """Get active predictions widget."""
        if not brain or not hasattr(brain, 'consciousness') or not brain.consciousness:
            return {
                "name": "Predictions",
                "type": "predictions",
                "data": {"predictions": [], "accuracy": 0}
            }
        
        consciousness = brain.consciousness
        active_preds = consciousness.prediction.active_predictions if hasattr(consciousness, 'prediction') else []
        
        return {
            "name": "Predictions",
            "type": "predictions",
            "data": {
                "predictions": [
                    {
                        "content": p.content,
                        "confidence": p.confidence,
                        "basis": p.basis,
                        "was_correct": p.was_correct
                    }
                    for p in active_preds[-5:]
                ],
                "accuracy": consciousness.prediction.prediction_accuracy if hasattr(consciousness, 'prediction') else 0,
                "total": consciousness.prediction.total_predictions if hasattr(consciousness, 'prediction') else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agents_widget(self, agents: list) -> Dict[str, Any]:
        """Get council agents widget."""
        return self.get_agent_widget(agents)
    
    def get_uptime(self) -> str:
        """Get system uptime."""
        uptime = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

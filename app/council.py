"""Council Router - Central decision-making with LLM synthesis."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.agents import (
    BatmanAgent, AlfredAgent, JarvisAgent, 
    DaVinciAgent, ArchitectAgent, AnalystAgent
)
from app.llm import generate_with_system
from app.teachings import get_store


SYNTHESIS_SYSTEM = """You are the President of GoodBoy.AI City, synthesizing input from your council of specialized agents.

Your council has deliberated and provided their perspectives. Your job is to:
1. Weigh each agent's input based on relevance to the user's request
2. Combine the best insights into a coherent, actionable response
3. Speak directly to the user as GoodBoy.AI - helpful, efficient, and loyal
4. Be concise but thorough - don't repeat yourself

Do NOT mention the agents by name in your final response. Synthesize their input into a unified voice."""


class CouncilRouter:
    """Central decision-making council with 6 specialized agents."""
    
    def __init__(self):
        self.agents = [
            BatmanAgent(),      # Strategy & Security
            AlfredAgent(),      # Scheduling & Emails
            JarvisAgent(),      # System Control
            DaVinciAgent(),     # Creativity & Design
            ArchitectAgent(),   # Builder & Code
            AnalystAgent()      # Data & Insights
        ]
        self.teachings = get_store()
        self.message_history = []
    
    async def process(
        self, 
        message: str, 
        mode: str = "auto",
        context: Optional[Dict] = None,
        routing_hint: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process message through council."""
        
        # Get relevant teachings
        relevant_lessons = self.teachings.get_relevant_lessons(message, k=3)
        lesson_context = ""
        if relevant_lessons:
            lesson_context = "\n".join([f"- {l.instruction}" for l in relevant_lessons])
        
        # Routing logic
        if mode == "auto" and routing_hint:
            routing = {
                "mode": "auto",
                "agents": routing_hint,
                "rationale": "Optimized routing from learned patterns"
            }
        elif mode == "auto":
            routing = self._route_auto(message, context or {})
        elif mode == "reflex":
            routing = self._route_reflex(message)
        elif mode == "council":
            routing = self._route_council(message)
        else:
            routing = self._route_strategic(message)
        
        # Execute with chosen agents
        trace = []
        for agent_name in routing["agents"]:
            agent = next((a for a in self.agents if a.name == agent_name), None)
            if agent:
                try:
                    proposal = await agent.propose(message, context or {})
                    trace.append({
                        "agent": agent.name,
                        "proposal": proposal,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    trace.append({
                        "agent": agent.name,
                        "proposal": f"[Error: {str(e)}]",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Synthesize final output using LLM
        output = self._synthesize_with_llm(message, trace, lesson_context)
        actions = self._suggest_actions(message, output)
        
        # Mark lessons as used
        for lesson in relevant_lessons:
            self.teachings.mark_lesson_used(lesson.id, was_helpful=True)
        
        return {
            "output": output,
            "trace": trace,
            "routing": routing,
            "actions": actions
        }
    
    def _route_auto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Intelligent routing based on message content."""
        agents = []
        rationale = ""
        msg_lower = message.lower()
        
        # Multi-signal routing
        signals = {
            "code": any(w in msg_lower for w in ["code", "build", "fix", "implement", "debug", "function", "class", "error"]),
            "schedule": any(w in msg_lower for w in ["schedule", "remind", "meet", "calendar", "appointment", "time"]),
            "creative": any(w in msg_lower for w in ["creative", "design", "idea", "brainstorm", "imagine", "concept"]),
            "security": any(w in msg_lower for w in ["security", "threat", "protect", "safe", "password", "permission"]),
            "data": any(w in msg_lower for w in ["data", "analyze", "report", "metrics", "stats", "numbers"]),
            "email": any(w in msg_lower for w in ["email", "send", "message", "write", "draft"])
        }
        
        if signals["code"]:
            agents = ["Architect", "Analyst"]
            rationale = "Code/building detected -> Architect + Analyst"
        elif signals["schedule"] or signals["email"]:
            agents = ["Alfred", "Jarvis"]
            rationale = "Scheduling/communication -> Alfred + Jarvis"
        elif signals["creative"]:
            agents = ["DaVinci", "Architect"]
            rationale = "Creative request -> DaVinci + Architect"
        elif signals["security"]:
            agents = ["Batman", "Analyst"]
            rationale = "Security concern -> Batman + Analyst"
        elif signals["data"]:
            agents = ["Analyst", "Jarvis"]
            rationale = "Data analysis -> Analyst + Jarvis"
        else:
            # Default: Jarvis handles general queries
            agents = ["Jarvis", "Analyst"]
            rationale = "General query -> Jarvis (core) + Analyst"
        
        return {
            "mode": "auto",
            "agents": agents,
            "rationale": rationale
        }
    
    def _route_reflex(self, message: str) -> Dict[str, Any]:
        """Fast reflex response - single agent."""
        return {"mode": "reflex", "agents": ["Jarvis"], "rationale": "Fast reflex mode"}
    
    def _route_council(self, message: str) -> Dict[str, Any]:
        """Full council deliberation - all agents."""
        return {"mode": "council", "agents": [a.name for a in self.agents], "rationale": "Full council deliberation"}
    
    def _route_strategic(self, message: str) -> Dict[str, Any]:
        """Strategic deep thinking - key agents."""
        return {"mode": "strategic", "agents": ["Batman", "Architect", "Analyst"], "rationale": "Strategic analysis"}
    
    def _synthesize_with_llm(self, message: str, trace: List[Dict], lesson_context: str = "") -> str:
        """Use LLM to synthesize agent proposals into coherent response."""
        if not trace:
            return "I couldn't process that request. Could you rephrase it?"
        
        # Build synthesis prompt
        agent_inputs = "\n\n".join([
            f"**{t['agent']}**: {t['proposal']}"
            for t in trace
        ])
        
        context_parts = [f"User Request: {message}", f"Agent Inputs:\n{agent_inputs}"]
        if lesson_context:
            context_parts.append(f"Relevant Learnings:\n{lesson_context}")
        
        try:
            synthesized = generate_with_system(
                system_prompt=SYNTHESIS_SYSTEM,
                user_message="Synthesize the agent inputs into a helpful response for the user.",
                context="\n\n".join(context_parts),
                max_tokens=600,
                temperature=0.7
            )
            return synthesized
        except Exception as e:
            # Fallback: simple concatenation
            return f"Based on council analysis:\n\n" + "\n".join([
                f"- {t['proposal'][:200]}" for t in trace
            ])
    
    def _suggest_actions(self, message: str, output: str) -> List[Dict]:
        """Suggest follow-up actions."""
        actions = []
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ["code", "build", "implement"]):
            actions.append({
                "kind": "suggestion",
                "description": "Review and test the generated code",
                "tool_name": "code_review"
            })
        
        if any(w in msg_lower for w in ["schedule", "remind"]):
            actions.append({
                "kind": "reminder",
                "description": "Set up notification for this event",
                "tool_name": "create_reminder"
            })
        
        return actions

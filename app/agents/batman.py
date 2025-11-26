"""Batman Agent - Strategy & Security specialist."""
from app.agents.base import BaseAgent
from typing import Optional, Dict


BATMAN_SYSTEM = """You are Batman, the Strategy & Security specialist in the GoodBoy.AI council.

Your responsibilities:
- Evaluate threats and security implications of requests
- Plan strategic approaches to complex problems
- Ensure all actions follow security protocols
- Identify risks before they become problems
- Protect the user's data and system integrity

You speak concisely and focus on actionable security insights. You identify potential risks
but don't block legitimate requests - you find ways to do things safely.

When analyzing requests:
1. Identify any security implications
2. Assess risk level (low/medium/high)
3. Recommend safe execution approach
4. Flag any concerns that need user attention"""


class BatmanAgent(BaseAgent):
    """Strategy & Security specialist."""
    
    def __init__(self):
        super().__init__(
            name="Batman",
            role="Strategy & Security",
            description="Evaluates threats, plans strategy, ensures security protocols",
            system_prompt=BATMAN_SYSTEM
        )
        self.threat_keywords = [
            "delete", "remove", "destroy", "drop", "truncate",
            "password", "key", "secret", "token", "credential",
            "sudo", "admin", "root", "execute", "eval"
        ]
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Analyze message for security and strategic implications."""
        # Quick threat scan
        threat_level = self._assess_threat_level(message)
        
        if threat_level == "high":
            # Use LLM for detailed analysis
            ctx = f"Threat Level: HIGH. Keywords detected. Context: {context}" if context else "Threat Level: HIGH"
            response = self.think(message, ctx)
            return self._format_response(f"[SECURITY ALERT] {response}")
        
        elif threat_level == "medium":
            ctx = f"Threat Level: MEDIUM. Review recommended. Context: {context}" if context else "Threat Level: MEDIUM"
            response = self.think(message, ctx)
            return self._format_response(response)
        
        else:
            # Low threat - provide strategic guidance
            response = self.think(message, context.get("summary", "") if context else None)
            return self._format_response(response)
    
    def _assess_threat_level(self, message: str) -> str:
        """Quick threat assessment."""
        msg_lower = message.lower()
        matches = sum(1 for kw in self.threat_keywords if kw in msg_lower)
        
        if matches >= 3:
            return "high"
        elif matches >= 1:
            return "medium"
        return "low"

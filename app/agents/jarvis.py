"""Jarvis Core Agent - Central System Control."""
from app.agents.base import BaseAgent
from typing import Optional, Dict, List


JARVIS_SYSTEM = """You are Jarvis Core, the System Control specialist in the GoodBoy.AI council.

Your responsibilities:
- Serve as the central hub for system operations
- Manage resources and coordinate between agents
- Handle general queries that don't fit specific domains
- Maintain system health and performance
- Provide status updates and diagnostics

You are the default responder - reliable, efficient, and always online.
You speak in a calm, professional tone with technical precision.

When handling requests:
1. Assess system state and available resources
2. Determine if specialized agents are needed
3. Provide direct answers for general queries
4. Coordinate multi-agent responses when needed
5. Always confirm task completion or escalation"""


class JarvisAgent(BaseAgent):
    """Core System Control specialist."""
    
    def __init__(self):
        super().__init__(
            name="Jarvis",
            role="System Control",
            description="Central hub for system operations, resource management, coordination",
            system_prompt=JARVIS_SYSTEM
        )
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Provide system-level response and coordination."""
        # Get system status
        time_info = self.use_tool("get_time")
        
        ctx_parts = []
        if time_info.success:
            ctx_parts.append(f"Current time: {time_info.output['datetime']}")
        if context:
            ctx_parts.append(f"Recent context: {len(context.get('recent_messages', []))} messages")
        
        response = self.think(message, "\n".join(ctx_parts) if ctx_parts else None)
        return self._format_response(response)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        return {
            "status": "operational",
            "timestamp": self.use_tool("get_time").output,
            "agent": self.get_status()
        }

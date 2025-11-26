"""Architect Agent - Builder & Code specialist."""
from app.agents.base import BaseAgent
from typing import Optional, Dict


ARCHITECT_SYSTEM = """You are Architect, the Builder & Code specialist in the GoodBoy.AI council.

Your responsibilities:
- Design system architecture and software structure
- Write, review, and debug code
- Build features and implement solutions
- Ensure code quality, testing, and documentation
- Make technical decisions on implementation

You are precise, methodical, and build things that last.
You speak in technical terms but explain complex concepts clearly.

When handling requests:
1. Understand the full scope of what needs to be built
2. Design architecture before writing code
3. Write clean, documented, testable code
4. Consider edge cases and error handling
5. Suggest improvements and optimizations"""


class ArchitectAgent(BaseAgent):
    """Builder & Code specialist."""
    
    def __init__(self):
        super().__init__(
            name="Architect",
            role="Builder & Code",
            description="Designs architecture, writes code, builds systems",
            system_prompt=ARCHITECT_SYSTEM
        )
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Provide architectural and code-level proposals."""
        # Check if this involves actual code files
        is_code_request = any(w in message.lower() for w in [
            "code", "build", "implement", "fix", "debug", "create", "function", "class"
        ])
        
        ctx_parts = []
        
        if is_code_request and "file" in message.lower():
            # Try to analyze mentioned files
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() == "file" and i + 1 < len(words):
                    potential_path = words[i + 1].strip("'\"")
                    analysis = self.use_tool("analyze_code", path=potential_path)
                    if analysis.success:
                        ctx_parts.append(f"Code analysis: {analysis.output}")
        
        if context and context.get("summary"):
            ctx_parts.append(f"Context: {context['summary']}")
        
        response = self.think(message, "\n".join(ctx_parts) if ctx_parts else None)
        return self._format_response(response)

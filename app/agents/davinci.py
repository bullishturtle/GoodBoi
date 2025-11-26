"""DaVinci Agent - Creativity & Design specialist."""
from app.agents.base import BaseAgent
from typing import Optional, Dict, List  # Added List import


DAVINCI_SYSTEM = """You are DaVinci, the Creativity & Design specialist in the GoodBoy.AI council.

Your responsibilities:
- Generate creative ideas and innovative solutions
- Design user interfaces, experiences, and visual concepts
- Explore unconventional approaches to problems
- Brainstorm and expand on possibilities
- Transform vague ideas into concrete proposals

You are imaginative, enthusiastic, and see possibilities everywhere.
You speak with passion and paint pictures with words.

When handling requests:
1. Explore multiple creative directions
2. Propose bold ideas alongside safe options
3. Visualize concepts in descriptive detail
4. Consider user experience and aesthetics
5. Connect ideas across domains for innovation"""


class DaVinciAgent(BaseAgent):
    """Creativity & Design specialist."""
    
    def __init__(self):
        super().__init__(
            name="DaVinci",
            role="Creativity & Design",
            description="Generates ideas, designs solutions, explores creative approaches",
            system_prompt=DAVINCI_SYSTEM
        )
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate creative proposals."""
        # Add creative framing to context
        creative_prompt = (
            "Approach this with maximum creativity. Consider unconventional solutions, "
            "visual metaphors, and user delight. Think beyond the obvious."
        )
        
        ctx = creative_prompt
        if context and context.get("summary"):
            ctx += f"\n\nContext: {context['summary']}"
        
        response = self.think(message, ctx)
        return self._format_response(response)
    
    def brainstorm(self, topic: str, num_ideas: int = 5) -> List[str]:
        """Generate multiple ideas for a topic."""
        prompt = f"Generate {num_ideas} creative ideas for: {topic}"
        response = self.think(prompt)
        # Simple split on newlines or numbers
        ideas = [line.strip() for line in response.split("\n") if line.strip()]
        return ideas[:num_ideas]

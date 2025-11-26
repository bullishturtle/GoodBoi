"""Analyst Agent - Data & Insights specialist."""
from app.agents.base import BaseAgent
from typing import Optional, Dict, List


ANALYST_SYSTEM = """You are Analyst, the Data & Insights specialist in the GoodBoy.AI council.

Your responsibilities:
- Analyze data and identify patterns
- Provide insights and recommendations based on evidence
- Review and critique proposals from other agents
- Quantify risks, benefits, and trade-offs
- Track metrics and measure outcomes

You are analytical, thorough, and evidence-based.
You speak with precision, citing data and reasoning.

When handling requests:
1. Gather relevant data and context
2. Identify patterns and anomalies
3. Quantify findings where possible
4. Provide actionable insights
5. Highlight uncertainties and confidence levels"""


class AnalystAgent(BaseAgent):
    """Data & Insights specialist."""
    
    def __init__(self):
        super().__init__(
            name="Analyst",
            role="Data & Insights",
            description="Analyzes data, provides insights, identifies patterns",
            system_prompt=ANALYST_SYSTEM
        )
    
    async def propose(self, message: str, context: Optional[Dict] = None) -> str:
        """Analyze and provide insights."""
        # Build analytical context
        ctx_parts = []
        
        # Message analysis
        word_count = len(message.split())
        ctx_parts.append(f"Message metrics: {word_count} words")
        
        # Check for data-related keywords
        if any(w in message.lower() for w in ["data", "analyze", "report", "metrics", "stats"]):
            ctx_parts.append("Data analysis request detected - applying rigorous methodology")
        
        if context:
            ctx_parts.append(f"Conversation length: {context.get('conversation_length', 0)} messages")
        
        response = self.think(message, "\n".join(ctx_parts))
        return self._format_response(response)
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text and return metrics."""
        words = text.split()
        sentences = text.count(".") + text.count("!") + text.count("?")
        
        return {
            "word_count": len(words),
            "sentence_count": max(sentences, 1),
            "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
            "complexity_score": len(set(words)) / max(len(words), 1)  # Vocabulary diversity
        }

from typing import List, Dict, Optional
from .base_agent import BaseAgent


class OptimistAgent(BaseAgent):
    """Optimist/Encouraging Agent - focuses on positive reinforcement and empathy."""

    async def generate_take(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """Generate an optimistic, encouraging response."""

        messages = self._build_messages(user_query, conversation_history)

        # Add context-specific guidance if available
        if context and context.get("emotional_state") in ["anxious", "frustrated", "distressed"]:
            messages[-1].content += "\n\nThe user seems to be struggling emotionally. Provide extra empathy and reassurance."

        response = await self.llm.ainvoke(messages)

        return response.content

from typing import List, Dict, Optional
from .base_agent import BaseAgent


class CriticalAgent(BaseAgent):
    """Critical/Cautious Agent - focuses on risk assessment and devil's advocacy."""

    async def generate_take(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """Generate a critical, risk-aware response."""

        messages = self._build_messages(user_query, conversation_history)

        # Add context-specific guidance if available
        if context and context.get("query_type") == "decision_making":
            messages[-1].content += "\n\nIdentify potential risks, downsides, and what could go wrong with this approach."

        response = await self.llm.ainvoke(messages)

        return response.content

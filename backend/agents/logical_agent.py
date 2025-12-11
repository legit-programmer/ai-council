from typing import List, Dict, Optional
from .base_agent import BaseAgent


class LogicalAgent(BaseAgent):
    """Logical/Data-Driven Agent - focuses on facts and objective analysis."""

    async def generate_take(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """Generate a logical, data-driven response."""

        messages = self._build_messages(user_query, conversation_history)

        # Add context-specific guidance if available
        if context and context.get("query_type") == "decision_making":
            messages[-1].content += "\n\nFocus on providing a structured analysis with pros/cons and data points."

        response = await self.llm.ainvoke(messages)

        return response.content

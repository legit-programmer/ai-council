from typing import List, Dict, Optional


class AgentMemory:
    """Individual memory for each agent - maintains their perspective."""

    def __init__(self, agent_name: str, max_length: int = 20):
        self.agent_name = agent_name
        self.max_length = max_length
        self.messages: List[Dict[str, str]] = []

    def add_exchange(self, user_query: str, agent_response: str):
        """Add a user query and the agent's own response."""
        self.messages.append({
            "role": "user",
            "content": user_query
        })
        self.messages.append({
            "role": "assistant",
            "content": agent_response
        })

        # Trim to max length
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length:]

    def notify_selected_response(self, user_query: str, selected_response: str, was_mine: bool):
        """
        Notify this agent about what response was actually sent to the user.
        This keeps all agents synchronized with the actual conversation.
        """
        if not was_mine:
            # Update memory with the selected response instead of this agent's take
            self.messages.append({
                "role": "user",
                "content": user_query
            })
            self.messages.append({
                "role": "assistant",
                "content": selected_response,
                "metadata": "selected_by_moderator"
            })

            # Trim to max length
            if len(self.messages) > self.max_length:
                self.messages = self.messages[-self.max_length:]

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history for this agent."""
        if last_n:
            return self.messages[-last_n:]
        return self.messages

    def clear(self):
        """Clear agent memory."""
        self.messages = []

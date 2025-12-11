from typing import Dict, List, Optional
from .agent_memory import AgentMemory
from .shared_memory import MainDiscussion


class MemoryManager:
    """
    Manages both agent-specific memories and the shared main discussion.
    Implements the notify mechanism to keep all agents in sync.
    """

    def __init__(self):
        # Individual agent memories
        self.agent_memories: Dict[str, AgentMemory] = {
            "logical": AgentMemory("logical"),
            "optimist": AgentMemory("optimist"),
            "critical": AgentMemory("critical")
        }

        # Shared main discussion
        self.main_discussion = MainDiscussion()

    def process_council_response(
        self,
        user_query: str,
        takes: List[Dict],
        final_response: str,
        selected_perspective: Optional[str],
        decision_metadata: Dict
    ):
        """
        Process a complete council exchange:
        1. Update main discussion with final response
        2. Notify all agents about the selected response
        """

        # Add to main discussion
        self.main_discussion.add_exchange(
            user_query=user_query,
            final_response=final_response,
            decision_metadata=decision_metadata
        )

        # Notify each agent
        takes_by_perspective = {t["perspective"]: t["response"] for t in takes}

        for perspective, agent_memory in self.agent_memories.items():
            agent_response = takes_by_perspective.get(perspective, "")
            was_selected = (perspective == selected_perspective)

            if was_selected:
                # This agent's response was selected - store their own response
                agent_memory.add_exchange(user_query, agent_response)
            else:
                # Another agent's response was selected - notify this agent
                agent_memory.notify_selected_response(
                    user_query=user_query,
                    selected_response=final_response,
                    was_mine=False
                )

    def get_conversation_history(self, last_n: Optional[int] = 5) -> List[Dict[str, str]]:
        """Get recent conversation history from main discussion."""
        return self.main_discussion.get_history(last_n)

    def get_agent_history(self, perspective: str, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history for a specific agent."""
        if perspective in self.agent_memories:
            return self.agent_memories[perspective].get_history(last_n)
        return []

    def clear_all(self):
        """Clear all memories."""
        for agent_memory in self.agent_memories.values():
            agent_memory.clear()
        self.main_discussion.clear()


# Global memory manager instance
memory_manager = MemoryManager()

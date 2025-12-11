from typing import List, Dict, Optional


class MainDiscussion:
    """
    Shared conversation memory - the "true" state of the conversation.
    This is what was actually said to the user (not the internal agent takes).
    """

    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        self.messages: List[Dict[str, str]] = []
        self.metadata: List[Dict] = []  # Track which agent/decision was used

    def add_exchange(
        self,
        user_query: str,
        final_response: str,
        decision_metadata: Optional[Dict] = None
    ):
        """Add a user query and the final response sent to user."""
        self.messages.append({
            "role": "user",
            "content": user_query
        })
        self.messages.append({
            "role": "assistant",
            "content": final_response
        })

        # Store metadata about the decision
        if decision_metadata:
            self.metadata.append(decision_metadata)

        # Trim to max length
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length:]
            # Also trim metadata
            if len(self.metadata) > self.max_length // 2:
                self.metadata = self.metadata[-self.max_length // 2:]

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get the main conversation history."""
        if last_n:
            return self.messages[-last_n:]
        return self.messages

    def get_last_decision(self) -> Optional[Dict]:
        """Get metadata about the last moderator decision."""
        if self.metadata:
            return self.metadata[-1]
        return None

    def clear(self):
        """Clear main discussion memory."""
        self.messages = []
        self.metadata = []

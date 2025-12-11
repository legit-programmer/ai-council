from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import yaml


class BaseAgent(ABC):
    """Abstract base class for all council agents."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.5
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature
        )
        self.memory: List[Dict[str, str]] = []

    @abstractmethod
    def generate_take(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """Generate a response from this agent's perspective."""
        pass

    def update_memory(self, user_query: str, response: str):
        """Update the agent's conversation memory."""
        self.memory.append({
            "role": "user",
            "content": user_query
        })
        self.memory.append({
            "role": "assistant",
            "content": response
        })

        # Keep memory to a reasonable size
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]

    def _build_messages(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]]
    ) -> List:
        """Build message list for LLM with system prompt and context."""
        messages = [SystemMessage(content=self.system_prompt)]

        # Add relevant conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add current query
        messages.append(HumanMessage(content=user_query))

        return messages


def load_agent_config() -> Dict:
    """Load agent configurations from YAML file."""
    config_path = "config/agents.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

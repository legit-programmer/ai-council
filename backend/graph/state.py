from typing import TypedDict, List, Dict, Optional, Literal, Annotated
from operator import add


class AgentTake(TypedDict):
    """Individual agent's response."""
    perspective: Literal["logical", "optimist", "critical"]
    response: str
    confidence: float


class CouncilState(TypedDict):
    """State for the council graph - shared across all nodes."""

    # Input
    user_query: str
    conversation_history: List[Dict[str, str]]

    # Context Analysis
    emotional_state: Optional[str]
    query_type: Optional[str]

    # Agent Takes (uses add reducer for parallel aggregation)
    takes: Annotated[List[AgentTake], add]

    # Moderator Output
    evaluation: Optional[Dict]
    decision: Optional[Literal["SELECT", "SYNTHESIZE"]]
    final_response: Optional[str]
    selected_perspective: Optional[str]
    synthesis_sources: Optional[List[str]]
    reasoning: Optional[str]

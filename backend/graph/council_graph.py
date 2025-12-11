from langgraph.graph import StateGraph, START, END
from typing import Dict
from .state import CouncilState, AgentTake
from .nodes import analyze_context_node
from ..agents import LogicalAgent, OptimistAgent, CriticalAgent, load_agent_config
from ..agents.moderator import ModeratorAgent


# Initialize agents from config
config = load_agent_config()

logical_agent = LogicalAgent(
    name=config["agents"]["logical"]["name"],
    system_prompt=config["agents"]["logical"]["system_prompt"],
    model=config["agents"]["logical"]["model"],
    temperature=config["agents"]["logical"]["temperature"]
)

optimist_agent = OptimistAgent(
    name=config["agents"]["optimist"]["name"],
    system_prompt=config["agents"]["optimist"]["system_prompt"],
    model=config["agents"]["optimist"]["model"],
    temperature=config["agents"]["optimist"]["temperature"]
)

critical_agent = CriticalAgent(
    name=config["agents"]["critical"]["name"],
    system_prompt=config["agents"]["critical"]["system_prompt"],
    model=config["agents"]["critical"]["model"],
    temperature=config["agents"]["critical"]["temperature"]
)

moderator_agent = ModeratorAgent()


# Node Functions

async def logical_agent_node(state: CouncilState) -> Dict:
    """Logical agent generates its take."""
    response = await logical_agent.generate_take(
        user_query=state["user_query"],
        conversation_history=state["conversation_history"],
        context={
            "emotional_state": state.get("emotional_state"),
            "query_type": state.get("query_type")
        }
    )

    take: AgentTake = {
        "perspective": "logical",
        "response": response,
        "confidence": 0.8
    }

    return {"takes": [take]}


async def optimist_agent_node(state: CouncilState) -> Dict:
    """Optimist agent generates its take."""
    response = await optimist_agent.generate_take(
        user_query=state["user_query"],
        conversation_history=state["conversation_history"],
        context={
            "emotional_state": state.get("emotional_state"),
            "query_type": state.get("query_type")
        }
    )

    take: AgentTake = {
        "perspective": "optimist",
        "response": response,
        "confidence": 0.8
    }

    return {"takes": [take]}


async def critical_agent_node(state: CouncilState) -> Dict:
    """Critical agent generates its take."""
    response = await critical_agent.generate_take(
        user_query=state["user_query"],
        conversation_history=state["conversation_history"],
        context={
            "emotional_state": state.get("emotional_state"),
            "query_type": state.get("query_type")
        }
    )

    take: AgentTake = {
        "perspective": "critical",
        "response": response,
        "confidence": 0.8
    }

    return {"takes": [take]}


async def moderator_node(state: CouncilState) -> Dict:
    """Moderator evaluates takes and selects/synthesizes final response."""
    result = await moderator_agent.evaluate_and_select(
        user_query=state["user_query"],
        takes=state["takes"],
        emotional_state=state.get("emotional_state", "neutral"),
        query_type=state.get("query_type", "information_seeking"),
        conversation_history=state["conversation_history"]
    )

    return {
        "evaluation": result["evaluation"],
        "decision": result["decision"],
        "final_response": result["final_response"],
        "selected_perspective": result.get("selected_perspective"),
        "synthesis_sources": result.get("synthesis_sources"),
        "reasoning": result["reasoning"]
    }


# Build the Graph

def create_council_graph():
    """Create and compile the council graph."""

    graph = StateGraph(CouncilState)

    # Add nodes
    graph.add_node("analyze_context", analyze_context_node)
    graph.add_node("logical_agent", logical_agent_node)
    graph.add_node("optimist_agent", optimist_agent_node)
    graph.add_node("critical_agent", critical_agent_node)
    graph.add_node("moderator", moderator_node)

    # Define edges
    # Start -> Context Analysis
    graph.add_edge(START, "analyze_context")

    # Context Analysis -> All 3 agents in parallel
    graph.add_edge("analyze_context", "logical_agent")
    graph.add_edge("analyze_context", "optimist_agent")
    graph.add_edge("analyze_context", "critical_agent")

    # All agents -> Moderator (LangGraph waits for all to complete)
    graph.add_edge("logical_agent", "moderator")
    graph.add_edge("optimist_agent", "moderator")
    graph.add_edge("critical_agent", "moderator")

    # Moderator -> End
    graph.add_edge("moderator", END)

    return graph.compile()


# Create the compiled graph
council_graph = create_council_graph()

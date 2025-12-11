from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from .state import CouncilState


async def analyze_context_node(state: CouncilState) -> Dict:
    """Analyze user query to detect emotional state and query type."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Get recent conversation context
    history_summary = ""
    if state["conversation_history"]:
        recent = state["conversation_history"][-3:]
        history_summary = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in recent])

    analysis_prompt = f"""
Analyze this user query and conversation history to understand context.

**User Query:** {state["user_query"]}

**Recent History:**
{history_summary if history_summary else "None"}

Return a JSON object with:
{{
    "emotional_state": "anxious|curious|frustrated|neutral|excited|distressed",
    "query_type": "decision_making|information_seeking|emotional_support|problem_solving"
}}

Only respond with valid JSON, no other text.
"""

    try:
        response = await llm.ainvoke([
            SystemMessage(
                content="You are a context analyzer. Always respond with valid JSON only."),
            HumanMessage(content=analysis_prompt)
        ])

        analysis = json.loads(response.content)

        return {
            "emotional_state": analysis.get("emotional_state", "neutral"),
            "query_type": analysis.get("query_type", "information_seeking")
        }
    except Exception as e:
        # Fallback to neutral defaults if parsing fails
        return {
            "emotional_state": "neutral",
            "query_type": "information_seeking"
        }

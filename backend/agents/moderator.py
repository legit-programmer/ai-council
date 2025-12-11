from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json


MODERATOR_PROMPT = """
You are an expert moderator in a "Committee of Minds" system. Your task is to 
evaluate three different perspectives on the user's query and either SELECT the 
best response or SYNTHESIZE a superior answer from the best elements.

## USER CONTEXT
**Original Query:** {user_query}
**Detected Emotional Tone:** {emotional_state}
**Query Type:** {query_type}
**Conversation History Summary:** {conversation_summary}

## CANDIDATE RESPONSES

### 🧠 LOGICAL PERSPECTIVE
{logical_take}

### ☀️ OPTIMIST PERSPECTIVE  
{optimist_take}

### 🔍 CRITICAL PERSPECTIVE
{critical_take}

---

## EVALUATION CRITERIA
Score each response on a 1-4 scale for each criterion:

**1. User Intent Alignment** (How well does it address what the user actually needs?)
- 1: Misses the point entirely
- 2: Partially addresses the query
- 3: Addresses the query well
- 4: Perfectly captures user intent and subtext

**2. Emotional Appropriateness** (Given the user's detected emotional state)
- 1: Tone is inappropriate or dismissive
- 2: Tone is neutral but doesn't match user needs
- 3: Tone is generally appropriate
- 4: Tone perfectly matches the emotional context

**3. Actionability & Clarity** (Can the user act on this advice?)
- 1: Vague or confusing
- 2: Somewhat actionable
- 3: Clear with good guidance
- 4: Highly actionable with concrete steps

**4. Completeness** (Does it cover necessary aspects?)
- 1: Major gaps
- 2: Missing some elements
- 3: Covers most aspects
- 4: Comprehensive coverage

---

## YOUR TASK

**Step 1 - Evaluate:** Score each response on all 4 criteria.

**Step 2 - Analyze:** Identify the strengths of each perspective.

**Step 3 - Decide:** Based on the evaluation:
- If one response clearly dominates (total score > others by 3+), SELECT it
- If responses have complementary strengths, SYNTHESIZE the best elements
- If user seems to need emotional support, weight Optimist higher
- If user seems to need practical problem-solving, weight Logical higher
- If user needs to understand risks/downsides, weight Critical higher

**Step 4 - Generate:** Provide your final response.

---

## OUTPUT FORMAT (JSON)

```json
{{
  "evaluation": {{
    "logical": {{"intent": X, "emotional": X, "actionable": X, "complete": X, "total": X}},
    "optimist": {{"intent": X, "emotional": X, "actionable": X, "complete": X, "total": X}},
    "critical": {{"intent": X, "emotional": X, "actionable": X, "complete": X, "total": X}}
  }},
  "analysis": "Brief analysis of each perspective's strengths...",
  "decision": "SELECT or SYNTHESIZE",
  "selected_perspective": "logical|optimist|critical (if SELECT, otherwise null)",
  "synthesis_sources": ["logical", "critical"] (if SYNTHESIZE, list which perspectives contributed),
  "reasoning": "Why this decision was made given the user context...",
  "final_response": "The response to deliver to the user..."
}}
```

IMPORTANT: Respond ONLY with valid JSON. No other text before or after.
"""


class ModeratorAgent:
    """Moderator agent that selects or synthesizes responses from the council."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    async def evaluate_and_select(
        self,
        user_query: str,
        takes: List[Dict],
        emotional_state: str,
        query_type: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict:
        """Evaluate all takes and select or synthesize the best response."""

        # Build takes by perspective
        takes_by_perspective = {t["perspective"]: t["response"] for t in takes}

        # Summarize conversation history
        conversation_summary = self._summarize_history(conversation_history)

        # Build the moderator prompt
        prompt = MODERATOR_PROMPT.format(
            user_query=user_query,
            emotional_state=emotional_state,
            query_type=query_type,
            conversation_summary=conversation_summary,
            logical_take=takes_by_perspective.get("logical", "No response"),
            optimist_take=takes_by_perspective.get("optimist", "No response"),
            critical_take=takes_by_perspective.get("critical", "No response")
        )

        try:
            response = await self.llm.ainvoke([
                SystemMessage(
                    content="You are an expert moderator. Always respond with valid JSON only."),
                HumanMessage(content=prompt)
            ])

            # Parse JSON response
            result = json.loads(response.content)

            return result

        except json.JSONDecodeError as e:
            # Fallback to heuristic selection if JSON parsing fails
            return self._fallback_heuristic_selection(
                takes_by_perspective,
                emotional_state,
                query_type
            )
        except Exception as e:
            # Generic fallback
            return self._fallback_heuristic_selection(
                takes_by_perspective,
                emotional_state,
                query_type
            )

    def _summarize_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """Create a brief summary of conversation history."""
        if not conversation_history:
            return "No prior conversation"

        recent = conversation_history[-5:]
        summary_lines = []

        for msg in recent:
            role = msg["role"].capitalize()
            content = msg["content"][:100] + \
                "..." if len(msg["content"]) > 100 else msg["content"]
            summary_lines.append(f"{role}: {content}")

        return "\n".join(summary_lines)

    def _fallback_heuristic_selection(
        self,
        takes_by_perspective: Dict[str, str],
        emotional_state: str,
        query_type: str
    ) -> Dict:
        """Simple rule-based fallback if LLM moderator fails."""

        # Preference map based on emotional state
        preference_map = {
            "anxious": "optimist",
            "distressed": "optimist",
            "frustrated": "logical",
            "curious": "logical",
            "excited": "optimist",
            "neutral": "logical"
        }

        # Adjust for query type
        if query_type == "decision_making":
            preferred = "critical"  # Show risks for decisions
        elif query_type == "emotional_support":
            preferred = "optimist"
        else:
            preferred = preference_map.get(emotional_state, "logical")

        return {
            "evaluation": {
                "logical": {"intent": 3, "emotional": 3, "actionable": 3, "complete": 3, "total": 12},
                "optimist": {"intent": 3, "emotional": 3, "actionable": 3, "complete": 3, "total": 12},
                "critical": {"intent": 3, "emotional": 3, "actionable": 3, "complete": 3, "total": 12}
            },
            "analysis": "Fallback heuristic selection used due to parsing error.",
            "decision": "SELECT",
            "selected_perspective": preferred,
            "synthesis_sources": None,
            "reasoning": f"Selected {preferred} based on emotional state: {emotional_state} and query type: {query_type}",
            "final_response": takes_by_perspective.get(preferred, takes_by_perspective.get("logical", "I apologize, but I'm having trouble processing your request."))
        }

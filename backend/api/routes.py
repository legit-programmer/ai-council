from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pipeline import process_query
from memory import memory_manager
import httpx
from config import settings


router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    final_response: str
    decision: str
    selected_perspective: Optional[str]
    evaluation: dict
    reasoning: str
    emotional_state: str
    query_type: str


class AnamSessionRequest(BaseModel):
    persona_id: Optional[str] = None


class AnamSessionResponse(BaseModel):
    session_token: str
    session_id: str


@router.post("/query", response_model=QueryResponse)
async def text_query(request: QueryRequest):
    """Process a text query through the council."""
    try:
        result = await process_query(request.query)

        return QueryResponse(
            final_response=result["final_response"],
            decision=result["decision"],
            selected_perspective=result.get("selected_perspective"),
            evaluation=result["evaluation"],
            reasoning=result["reasoning"],
            emotional_state=result["emotional_state"],
            query_type=result["query_type"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history():
    """Get conversation history."""
    return {
        "main_discussion": memory_manager.get_conversation_history(last_n=10),
        "last_decision": memory_manager.main_discussion.get_last_decision()
    }


@router.delete("/history")
async def clear_history():
    """Clear all conversation history."""
    memory_manager.clear_all()
    return {"message": "History cleared"}


@router.post("/anam/session", response_model=AnamSessionResponse)
async def create_anam_session(request: AnamSessionRequest):
    """
    Create an Anam AI session token for the frontend.
    This handles server-side authentication with Anam API.
    """
    url = "https://api.anam.ai/v1/sessions"

    headers = {
        "Authorization": f"Bearer {settings.anam_api_key}",
        "Content-Type": "application/json"
    }

    # Configure persona for pass-through mode (custom LLM)
    payload = {
        "persona_id": request.persona_id if request.persona_id else "default",
        "config": {
            "llm_mode": "custom"  # Use custom LLM (our council)
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                return AnamSessionResponse(
                    session_token=data["session_token"],
                    session_id=data["session_id"]
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Anam API error: {response.text}"
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to connect to Anam API: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

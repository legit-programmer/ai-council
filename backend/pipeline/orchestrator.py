from typing import AsyncGenerator, Dict
from graph import council_graph
from memory import memory_manager


async def process_query(user_query: str) -> Dict:
    """
    Process a user query through the council of agents.

    Args:
        user_query: The user's input text

    Returns:
        Dictionary containing the final response and metadata
    """
    # Get conversation history from memory
    conversation_history = memory_manager.get_conversation_history(last_n=5)

    # Prepare initial state
    initial_state = {
        "user_query": user_query,
        "conversation_history": conversation_history,
        "emotional_state": None,
        "query_type": None,
        "takes": [],
        "evaluation": None,
        "decision": None,
        "final_response": None,
        "selected_perspective": None,
        "synthesis_sources": None,
        "reasoning": None
    }

    # Run through the council graph
    result = await council_graph.ainvoke(initial_state)

    # Update memory with the result
    memory_manager.process_council_response(
        user_query=user_query,
        takes=result["takes"],
        final_response=result["final_response"],
        selected_perspective=result.get("selected_perspective"),
        decision_metadata={
            "decision": result["decision"],
            "evaluation": result["evaluation"],
            "reasoning": result["reasoning"],
            "emotional_state": result["emotional_state"],
            "query_type": result["query_type"]
        }
    )

    return result


async def process_audio_to_text(audio_chunks: list[bytes]) -> str:
    """
    Process audio chunks to text via Whisper STT.

    Args:
        audio_chunks: List of audio byte chunks (2-second buffers)

    Returns:
        Transcribed text
    """
    from .stt import transcribe_audio_stream
    return await transcribe_audio_stream(audio_chunks)


async def process_text_to_audio(text: str) -> bytes:
    """
    Process text to audio via ElevenLabs TTS.

    Args:
        text: Text to convert to speech

    Returns:
        Audio bytes (MP3)
    """
    from .tts import text_to_speech
    return await text_to_speech(text)


async def process_full_pipeline(audio_chunks: list[bytes]) -> Dict:
    """
    Full pipeline: Audio -> Text -> Council -> Text -> Audio

    Args:
        audio_chunks: Audio input from user

    Returns:
        Dictionary with transcription, council response, and audio output
    """
    # Step 1: Audio to Text
    user_query = await process_audio_to_text(audio_chunks)

    if not user_query:
        return {
            "error": "Failed to transcribe audio",
            "transcription": "",
            "response": None,
            "audio": None
        }

    # Step 2: Process through council
    council_result = await process_query(user_query)

    # Step 3: Text to Audio
    audio_output = await process_text_to_audio(council_result["final_response"])

    return {
        "transcription": user_query,
        "response": council_result,
        "audio": audio_output
    }

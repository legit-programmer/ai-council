from openai import AsyncOpenAI
from config import settings
import base64


client = AsyncOpenAI(api_key=settings.openai_api_key)


async def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        audio_data: Raw audio bytes (PCM format from browser)

    Returns:
        Transcribed text
    """
    try:
        # Convert bytes to file-like object for OpenAI API
        # The audio should be in a supported format (webm, mp4, mp3, wav, etc.)
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.webm", audio_data),
            language="en"  # Optional: specify language for better accuracy
        )

        return response.text

    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""


async def transcribe_audio_stream(audio_chunks: list[bytes]) -> str:
    """
    Transcribe multiple audio chunks as a single stream.
    Useful for 2-second buffered chunks from VAD.

    Args:
        audio_chunks: List of audio byte chunks

    Returns:
        Transcribed text
    """
    # Combine chunks
    combined_audio = b"".join(audio_chunks)
    return await transcribe_audio(combined_audio)

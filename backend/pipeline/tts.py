import httpx
from config import settings


async def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs API.

    Args:
        text: Text to convert to speech

    Returns:
        Audio bytes (MP3 format)
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": settings.elevenlabs_api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)

            if response.status_code == 200:
                return response.content
            else:
                print(
                    f"ElevenLabs API error: {response.status_code} - {response.text}")
                return b""

    except Exception as e:
        print(f"Error generating speech: {e}")
        return b""


async def text_to_speech_stream(text: str):
    """
    Stream text-to-speech audio from ElevenLabs.
    Yields audio chunks as they're generated.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}/stream"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": settings.elevenlabs_api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data, headers=headers, timeout=30.0) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_bytes():
                        yield chunk
                else:
                    print(f"ElevenLabs API error: {response.status_code}")

    except Exception as e:
        print(f"Error streaming speech: {e}")

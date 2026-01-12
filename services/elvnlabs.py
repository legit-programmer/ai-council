from dotenv import load_dotenv
from elevenlabs.client import AsyncElevenLabs, ElevenLabs
from elevenlabs.play import play, stream
import asyncio
import os

load_dotenv()



elevenlabs = AsyncElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)


def synthesize_and_play_speech(text: str, voice_id: str):
    if isinstance(elevenlabs, ElevenLabs):
        audio = elevenlabs.text_to_speech.convert(text=text, voice_id=voice_id)
        play(audio)
    else:
        raise ValueError("Elevenlabs client instance is async not sync.")


async def asynthesize_and_return_speech(text: str, voice_id: str):
    async for i in elevenlabs.text_to_speech.stream(voice_id=voice_id, text=text):
        yield i



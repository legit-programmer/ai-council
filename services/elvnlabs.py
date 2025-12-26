from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

load_dotenv()

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def synthesize_and_play_speech(text: str, voice_id: str):
    audio =  elevenlabs.text_to_speech.convert(text=text, voice_id=voice_id)
    play(audio)

from faster_whisper import WhisperModel
import numpy as np
from pydub import AudioSegment
import io


# model = WhisperModel('small', device='cpu')


async def process_audio_chunk(chunk: bytes):
	pass # to be implemented
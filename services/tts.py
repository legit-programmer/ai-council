import asyncio
from pocket_tts import TTSModel
from concurrent.futures import ThreadPoolExecutor
from torch import Tensor
import numpy as np


class TextToSpeechService:
    def __init__(self):
        self.model: TTSModel = TTSModel.load_model()
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def asynthesize_speech(self, text: str, voice_id: str = "alba"):

        gen = self.model.generate_audio_stream(
            model_state=self.model.get_state_for_audio_prompt(voice_id), text_to_generate=text)
        loop = asyncio.get_running_loop()

        def generate_next_chunk(gen):
            try:
                chunk: Tensor = next(gen)
                return chunk, False
            except StopIteration:
                return None, True
        while True:
            chunk, done = await loop.run_in_executor(self.executor, generate_next_chunk, gen)
            if done:
                break
            audio_array = chunk.cpu().numpy()
            audio_int16 = (audio_array * 32767).astype(np.int16)
            yield audio_int16.tobytes()

        
service = None


def get_tts_service() -> TextToSpeechService:
    global service
    if service is None:
        service = TextToSpeechService()

    return service

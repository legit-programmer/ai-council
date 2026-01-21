import asyncio
from pocket_tts import TTSModel
from concurrent.futures import ThreadPoolExecutor


tts_model = TTSModel.load_model()


class TextToSpeechService:
    def __init__(self):
        self.model:TTSModel = TTSModel.load_model()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def asynthesize_speech(self, text: str, voice_id: str="alba"):

        def generate():
            return self.model.generate_audio_stream(model_state=self.model.get_state_for_audio_prompt(voice_id), text_to_generate=text)
        
        loop = asyncio.get_event_loop()
        audio_data = await loop.run_in_executor(self.executor, generate)
        for chunk in audio_data:
            yield chunk

    
async def main():
    tts = TextToSpeechService()
    text = """sample text"""
    async for i in tts.asynthesize_speech(text):
        print("Executed first instance")
    async for j in tts.asynthesize_speech(text):
        print("Executed second instance")

asyncio.run(main=main())
# import numpy as np
# import sounddevice as sd
# from faster_whisper import WhisperModel

# # Load small model for speed (use "tiny" for faster, "small" for better quality)
# model = WhisperModel("base", device="cpu")

# SAMPLE_RATE = 16000
# CHUNK_DURATION = 3  # seconds

# def transcribe_chunk(audio_chunk):
#     segments, _ = model.transcribe(audio_chunk, beam_size=1)
#     return " ".join([seg.text for seg in segments])

# def callback(indata, frames, time, status):
#     audio_buffer.extend(indata[:, 0])
    
#     if len(audio_buffer) >= SAMPLE_RATE * CHUNK_DURATION:
#         chunk = np.array(audio_buffer[:SAMPLE_RATE * CHUNK_DURATION], dtype=np.float32)
#         audio_buffer.clear()
        
#         text = transcribe_chunk(chunk)
#         if text.strip():
#             print(f">> {text}")

#     audio_buffer = []

#     with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
#         print("Listening... Press Ctrl+C to stop")
#         while True:
#             sd.sleep(100)
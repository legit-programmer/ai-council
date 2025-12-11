from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import base64
from pipeline import process_audio_to_text, process_query, process_text_to_audio


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def send_bytes(self, data: bytes, websocket: WebSocket):
        await websocket.send_bytes(data)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming.

    Protocol:
    - Client sends: {"type": "audio_chunk", "data": base64_audio}
    - Client sends: {"type": "audio_end"} when VAD detects end of speech
    - Server responds: {"type": "transcription", "text": "..."}
    - Server responds: {"type": "response", "data": {...}}
    - Server sends: {"type": "audio", "data": base64_audio}
    """
    await manager.connect(websocket)

    audio_buffer: List[bytes] = []

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_json()

            msg_type = message.get("type")

            if msg_type == "audio_chunk":
                # Accumulate audio chunks (2-second buffer from VAD)
                audio_data = base64.b64decode(message["data"])
                audio_buffer.append(audio_data)

            elif msg_type == "audio_end":
                # VAD detected end of speech, process accumulated audio
                if audio_buffer:
                    # Step 1: Transcribe audio
                    transcription = await process_audio_to_text(audio_buffer)

                    await manager.send_json({
                        "type": "transcription",
                        "text": transcription
                    }, websocket)

                    if transcription:
                        # Step 2: Process through council
                        council_result = await process_query(transcription)

                        await manager.send_json({
                            "type": "response",
                            "data": {
                                "final_response": council_result["final_response"],
                                "decision": council_result["decision"],
                                "selected_perspective": council_result.get("selected_perspective"),
                                "emotional_state": council_result["emotional_state"],
                                "reasoning": council_result["reasoning"]
                            }
                        }, websocket)

                        # Step 3: Generate TTS audio (this will be sent to Anam instead)
                        # Note: In pass-through mode, we send text to Anam, not audio
                        # But we can still generate audio if needed

                    # Clear buffer
                    audio_buffer = []

            elif msg_type == "text_query":
                # Direct text query (bypass audio pipeline)
                query = message.get("text")

                if query:
                    council_result = await process_query(query)

                    await manager.send_json({
                        "type": "response",
                        "data": {
                            "final_response": council_result["final_response"],
                            "decision": council_result["decision"],
                            "selected_perspective": council_result.get("selected_perspective"),
                            "emotional_state": council_result["emotional_state"],
                            "reasoning": council_result["reasoning"]
                        }
                    }, websocket)

            elif msg_type == "ping":
                # Heartbeat
                await manager.send_json({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

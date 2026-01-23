from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from starlette.types import Message
from services.models import Event, EventType
from services.whisper import process_audio_chunk
from services.loop import run_discussion_loop
from services.redis import get_redis_store
from asyncio.tasks import Task
import asyncio
import json
from json import JSONDecodeError


store = get_redis_store()

class ConnectionManager:
    def __init__(self):
        self.active_connection: dict[str, WebSocket] = {}
        self.active_sessions: dict[str, Task] = {}
        
    async def authenticate_connection(self, websocket: WebSocket):
        pass

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connection:
            self.active_connection[session_id] = websocket
        else:
            await websocket.send_text("Only 1 device can be connected per session.") 
            await websocket.close()
    
    async def recieve_and_handle_event(self, websocket: WebSocket, session_id: str):
        try:
            event = await self.validate_message_type(websocket)

            if not event:
                return 
            elif isinstance(event, bytes):
                await process_audio_chunk(event)
                return 
            

            session_active = session_id in self.active_sessions

            if event.type==EventType.START:
                if not session_active:
                    task = asyncio.create_task(run_discussion_loop(session_id, websocket))
                    self.active_sessions[session_id] = task
                    return await websocket.send_text("started")
                else:
                    return await websocket.send_denial_response("Session already active")
                
            if not session_active:
                return await websocket.send_text("No session running.")
            
            if event.type==EventType.STOP:
                self.active_sessions[session_id].cancel()
                print("Stopped session: ", session_id)
                return await websocket.send_text("Session stopped.")
            
            elif event.type==EventType.TEXT_INPUT:
                text: str = event.data
                if len(text.strip()) > 1:
                    store.add_user_message(session_id, text)
                    return await websocket.send_text('added to queue')
                
                return await websocket.send_text("invalid user input")

            elif event.type==EventType.PLAYING_AUDIO:
                store.set_is_playing(session_id, True)
                await websocket.send_text("is_playing set to True")
            
            elif event.type==EventType.DONE_PLAYING_AUDIO:
                store.set_is_playing(session_id, False)
                await websocket.send_text("is_playing set to False")
                
        except Exception as e:
            print(f'Error: {e}')
            await websocket.send_text("Not a valid event.")

    async def validate_message_type(self, websocket: WebSocket) -> Event | bytes | None:
        message = await websocket.receive()
        
        if message.get('type')=="websocket.receive":
            if 'text' in message:
                text = message['text']
                try:
                    json_text = json.loads(text)
                    return Event(**json_text)
                except JSONDecodeError:
                    await websocket.send_text("Invalid event format")
            elif 'bytes' in message:
                print('bytes recieved')
                return message['bytes']



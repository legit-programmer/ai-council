from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from starlette.types import Message
from services.models import Event, EventType
from services.loop import run_discussion_loop
from asyncio.tasks import Task
import json
from json import JSONDecodeError
from services.redis import get_redis_store


store = get_redis_store()
import asyncio
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
                return await self.process_audio_chunks()
            

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
                print('here')
                return message['bytes']


    async def process_audio_chunks(self):
        print('test process')

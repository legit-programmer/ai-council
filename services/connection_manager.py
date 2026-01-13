from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from services.models import Event, EventType
from services.loop import run_discussion_loop
from asyncio.tasks import Task
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
            raw_event = await websocket.receive_json()
            event = Event(**raw_event)
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
            print(e)
            await websocket.send_text("Not a valid event.")



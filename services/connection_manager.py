from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from services.models import Event, EventType
from services.agents import run_discussion_loop

import asyncio
class ConnectionManager:
    def __init__(self):
        self.active_connection = {}
        self.active_sessions = {}
        
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

            if event.type==EventType.START:
                if session_id not in self.active_sessions:
                    asyncio.create_task(run_discussion_loop(session_id))
                    await websocket.send_text("started")
                else:
                    await websocket.send_denial_response("Session already active")
            if event.type==EventType.STOP:
                print("stop")
        except Exception as e:
            print(e)
            await websocket.send_text("Not a valid event.")



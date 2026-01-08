from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from services.models import Event, EventType

class ConnectionManager:
    def __init__(self):
        self.active_connection = []
        self.active_sessions = []
        
    async def authenticate_connection(self, websocket: WebSocket):
        pass

    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)
    
    async def recieve_and_handle_event(self, websocket: WebSocket):
        try:
            raw_event = await websocket.receive_json()
            event = Event(**raw_event)

            if event.type==EventType.START:
                await websocket.send_text("started")
                
            if event.type==EventType.STOP:
                print("stop")
        except Exception as e:
            print(e)
            await websocket.send_text("Not a valid event.")



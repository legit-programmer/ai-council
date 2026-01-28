from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.models import CreateSession
from services.connection_manager import ConnectionManager
from fastapi.websockets import WebSocket
from services.redis import get_redis_store


app = FastAPI()
manager = ConnectionManager()
store = get_redis_store()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message":"AI-council live."}

@app.post("/create_session")
async def create_session(session: CreateSession):
    store.create_session(session_id=session.session_id, agents=session.agents, initial_user_input=session.initial_user_input)
    return {"message": "Session created successfully."}
    

@app.websocket('/ws/connect')
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.authenticate_connection(websocket)
    await manager.handle_connection(websocket, session_id)
    while True:
        await manager.recieve_and_handle_event(websocket, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
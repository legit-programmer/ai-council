from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from api import router, websocket_endpoint
from config import settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Council API",
    description="Multi-Agent Conversational AI with Committee of Minds",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(router, prefix="/api")

# WebSocket endpoint


@app.websocket("/ws")
async def websocket_route(websocket):
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    return {
        "message": "AI Council API",
        "docs": "/docs",
        "websocket": "/ws"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )

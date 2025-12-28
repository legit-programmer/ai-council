from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.agents import Agent, Orchestrator
from services.models import CreateSession

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_store = {}

@app.get("/")
async def read_root():
    return {"message":"AI-council live."}

async def create_session(session: CreateSession):
    if session.session_id in session_store:
        return {"error": "Session already exists."}
    
    
    agents = [Agent(name=agent.name, role=agent.role, traits=agent.traits) for agent in session.agents]
    orchestrator = Orchestrator(agents=agents)
    
    session_store[session.session_id] = {
        "orchestrator": orchestrator,
        "agents": agents
    }
    return {"message": "Session created successfully."}
    
    


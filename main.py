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

@app.post("/create_session")
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
    
@app.post("/inference/{session_id}")
async def inference_session_via_text(session_id: str, user_message: str):
    if session_id not in session_store:
        return {"error": "Session not found."}
    
    orchestrator = session_store[session_id]["orchestrator"]
    agents = session_store[session_id]["agents"]
    
    orchestrator_response = await orchestrator.inference(user_message)
    
    agent_responses = {}
    for agent in agents:
        agent_response = await agent.process_user_message(user_message)
        agent_responses[agent.name] = agent_response
    
    return {
        "orchestrator_response": orchestrator_response,
        "agent_responses": agent_responses
    }
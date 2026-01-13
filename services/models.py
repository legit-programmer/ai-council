from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from enum import Enum


class AgentConfig(BaseModel):
    name: str
    role: str
    traits: list[str]
    messages: list[dict] = []
    voice_id: str = None


class CreateSession(BaseModel):
    session_id: str
    agents: list[AgentConfig]

    @model_validator(mode="before")
    def check_roles_and_traits(cls, values):
        roles = values.get("roles", [])
        traits = values.get("traits", [])
        if len(roles) != len(traits):
            raise ValueError(
                "The number of roles must match the number of traits lists.")
        return values


class OrchestratorState(BaseModel):
    conversation_stacks: dict[str, list[str]] = {}
    user_alias: str = "MainUser"
    previous_author_index: int = -1


class UpdateSession(BaseModel):
    agents: list[AgentConfig]
    orchestrator_state: OrchestratorState


class SessionData(BaseModel):
    agents_state: list[AgentConfig]
    orchestrator_state: OrchestratorState
    pause: str
    stop: str


class EventType(str, Enum):
    START = 'START'
    STOP = 'STOP'
    TEXT_INPUT = 'TEXT_INPUT'


class Event(BaseModel):
    type: Literal["START", "STOP", "TEXT_INPUT"]
    data: Optional[str] = None

class AudioEvent(BaseModel):
    agent_name: str
    voice_id: str
from pydantic import BaseModel, model_validator

class AgentConfig(BaseModel):
    name: str
    role: str
    traits: list[str]

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
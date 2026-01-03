import redis
from services.models import AgentConfig, OrchestratorState
import ast
from services.prompts import SUB_AGENT_PROMPT

class RedisStore:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def create_session(self, session_id: str, agents: list[AgentConfig]):
        key = f'session:{session_id}'
        for agent in agents:
            if not isinstance(agent, AgentConfig):
                raise ValueError("All agents must be instances of AgentConfig")
            agent.messages.append({"role": "system", "content": SUB_AGENT_PROMPT.format(
                role=agent.role,
                traits=", ".join(agent.traits),
                user_input=""
            )})
        
        agents_state= [agent.model_dump() for agent in agents]

        orchestrator_state = OrchestratorState(
            conversation_stacks={agent.name: [] for agent in agents},
        ).model_dump()
        self.client.hset(key, mapping={'agents_state': str(agents_state)})
        self.client.hset(key, mapping={'orchestrator_state': str(orchestrator_state)})
        print(f"Session {session_id} created in Redis.")
    
    def get_session(self, session_id: str):
        key = f'session:{session_id}'
        agents_state: str = self.client.hget(key, 'agents_state').decode('utf-8')
        agents_state = ast.literal_eval(agents_state)
        agents_state = [AgentConfig.model_validate(agent) for agent in agents_state]
        orchestrator_state = self.client.hget(key, 'orchestrator_state').decode('utf-8')
        orchestrator_state = ast.literal_eval(orchestrator_state)
        orchestrator_state = OrchestratorState.model_validate(orchestrator_state)
        if agents_state and orchestrator_state:
            return {
                'agents_state': agents_state,
                'orchestrator_state': orchestrator_state
            }
        else:
            print(f"Session {session_id} not found in Redis.")
            return None

    def update_session(self, session_id: str, agents: list[AgentConfig], orchestrator_state: OrchestratorState):
        key = f'session:{session_id}'
        agents_state= [agent.model_dump() for agent in agents]
        self.client.hset(key, mapping={'agents_state': str(agents_state)})
        self.client.hset(key, mapping={'orchestrator_state': str(orchestrator_state.model_dump())})
        print(f"Session {session_id} updated in Redis.")
        
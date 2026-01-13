import redis
from services.models import AgentConfig, OrchestratorState, UpdateSession, SessionData
import ast
from services.prompts import SUB_AGENT_PROMPT
from services.agents import Agent, Orchestrator

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

        self.client.hset(key, mapping={'agents_state': str(agents_state),
                                    'orchestrator_state': str(orchestrator_state) ,
                                    'pause': 'false',
                                    'stop': 'false'

                                    })
        print(f"Session {session_id} created in Redis.")
    
    def get_session(self, session_id: str):
        key = f'session:{session_id}'
        agents_state = self.client.hget(key, 'agents_state').decode('utf-8')
        agents_state = ast.literal_eval(agents_state)
        agents_state = [AgentConfig.model_validate(agent) for agent in agents_state]
        orchestrator_state = self.client.hget(key, 'orchestrator_state').decode('utf-8')
        orchestrator_state = ast.literal_eval(orchestrator_state)
        orchestrator_state = OrchestratorState.model_validate(orchestrator_state)
        pause = ast.literal_eval(str(self.client.hget(key,'pause')))
        stop = ast.literal_eval(str(self.client.hget(key,'stop')))
        if agents_state and orchestrator_state:
            return SessionData(
                agents_state=agents_state,
                orchestrator_state=orchestrator_state,
                pause=pause,
                stop=stop
            )
        else:
            print(f"Session {session_id} not found in Redis.")
            return None

    def update_session(self, session_id: str, update_session: UpdateSession):
        key = f'session:{session_id}'
        agents_state= [agent.model_dump() for agent in update_session.agents]
        self.client.hset(key, mapping={'agents_state': str(agents_state),
                                       'orchestrator_state': str(update_session.orchestrator_state.model_dump())            })
        print(f"Session {session_id} updated in Redis.")

    def add_user_message(self, session_id: str, user_message: str):
        key = f'session:{session_id}:user_messages'
        self.client.rpush(key, user_message)
        print(f"User message added to session {session_id} in Redis.")

    def get_user_messages(self, session_id: str):
        key = f'session:{session_id}:user_messages'
        user_messages = self.client.lrange(key, 0, -1)
        user_messages = [msg.decode('utf-8') for msg in user_messages]
        return user_messages
    
    def clear_user_messages(self, session_id: str):
        key = f'session:{session_id}:user_messages'
        self.client.delete(key)
        print(f"User messages cleared for session {session_id} in Redis.")

    def stop_session(self, session_id: str):
        key = f'session:{session_id}'
        self.client.hset(key, 'stop', 'true')
        print(f"Session stopped for session {session_id} in Redis.")
    
    def pause_session(self, session_id: str):
        key = f'session:{session_id}'
        self.client.hset(key, 'pause', 'true')
        print(f"Session paused for session {session_id} in Redis.")

    def update_session_from_orchestrator(self, session_id: str, orchestrator: Orchestrator):
        self.update_session(
            session_id=session_id,
            update_session=UpdateSession(
                agents=[AgentConfig(  
                    name=agent.name,
                    role=agent.role,
                    traits=agent.traits,
                    messages=agent.messages,
                    voice_id=agent.voice_id
                ) for agent in orchestrator.agents],
                orchestrator_state=OrchestratorState(
                    conversation_stacks=orchestrator.conversation_stacks,
                    previous_author_index=orchestrator.previous_author_index
                )
            )
        )

instance = None

def get_redis_store():
    global instance
    if not instance:
        return RedisStore()
    return instance
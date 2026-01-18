
from services.redis import get_redis_store
from services.models import *
from services.agents import construct_orchestrator_from_state
from fastapi.websockets import WebSocket
from services.elvnlabs import asynthesize_and_return_speech

store = get_redis_store()
id = "session_123"
store.create_session(
    session_id=id, agents=[
        AgentConfig(name="Agent1", role="Tech Expert", traits=["Innovative", "Analytical"], voice_id="6WjhCXzqp2hnSqFtrG8P"),
        AgentConfig(name="Agent2", role="Business Strategist", traits=["Pragmatic", "Visionary"], voice_id="rAsfH6d68tmh0XRGXp4D"),
        AgentConfig(name="Agent3", role="Marketing Guru", traits=["Creative", "Persuasive"], voice_id="xNtG3W2oqJs0cJZuTyBc"),
    ])

id = "session_1234"
store.create_session(
    session_id=id, agents=[
        AgentConfig(name="Agent1", role="Tech Expert", traits=["Innovative", "Analytical"], voice_id="6WjhCXzqp2hnSqFtrG8P"),
        AgentConfig(name="Agent2", role="Business Strategist", traits=["Pragmatic", "Visionary"], voice_id="rAsfH6d68tmh0XRGXp4D"),
        AgentConfig(name="Agent3", role="Marketing Guru", traits=["Creative", "Persuasive"], voice_id="xNtG3W2oqJs0cJZuTyBc"),
    ])



async def run_discussion_loop(session_id:str, websocket: WebSocket, max_iterations: int = 100):
    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")
        #get session data
        session_data = store.get_session(session_id)
        
        if session_data.stop=='true':
            print("exiting gracefully") 
            break
        
        agents_state: list[AgentConfig] = session_data.agents_state
        orchestrator_state: OrchestratorState = session_data.orchestrator_state

        # reconstruct orchestrator
        orchestrator = construct_orchestrator_from_state(agents_state, orchestrator_state)

        # provide initial user input
        if iteration == 0:
            user_input = "count till 10 one by one"
            orchestrator.update_conversation_stacks(previous_take=user_input, previous_take_author=orchestrator.user_alias)

        agent_index, take = await orchestrator.decide_and_get_take()

        orchestrator.update_conversation_stacks(
        previous_take=take, previous_take_author=orchestrator.agents[agent_index].name)
        
        # response log
        agent = orchestrator.agents[agent_index]
        print(
            f"{agent.name} provided take: {take}")
        event = AudioEvent(agent_name=agent.name, voice_id=agent.voice_id, text=take).model_dump_json()
        await websocket.send_text(event)
        async for chunk in asynthesize_and_return_speech(text=take, voice_id=agent.voice_id):
            await websocket.send_bytes(chunk)
            
            

        # check and treat user queue
        # future improvement: implement pubsub and restart loop on new message event
        user_messages = store.get_user_messages(session_id=id)
        print(f"User messages in queue: {user_messages}")
        if len(user_messages) > 0:
            messages = ','.join(user_messages)
            orchestrator.update_conversation_stacks(
                previous_take=messages, previous_take_author=orchestrator.user_alias
            )
            store.clear_user_messages(session_id=id) # clear user messages after adding to the stacks


        # add more robust approach for updading state for eg only updating delta changes
        store.update_session_from_orchestrator(session_id=session_id, orchestrator=orchestrator)



import random
from services.prompts import SUB_AGENT_PROMPT, ORCHESTRATOR_PROMPT
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
from elevenlabs.play import play 
from services.models import AgentConfig, OrchestratorState
from services.elvnlabs import synthesize_and_play_speech as syn

import keyboard

from services.redis import RedisStore
load_dotenv()


class Agent:
    def __init__(self, name: str, role: str, traits: list = None, voice_id: str = None, messages: list = None):
        self.name = name
        self.role = role
        self.traits = traits if traits is not None else []
        self.messages = messages if messages is not None else []
        self.voice_id = voice_id
        self.llm = ChatOpenAI(model="gpt-5.2", reasoning=None)

    async def inference(self, message: str, role: str = "user"):
        self.messages.append({"role": role, "content": message})
        response = await self.llm.ainvoke(self.messages)
        self.messages.append(
            {"role": "assistant", "content": response.content})
        return response.content

    async def initialize_agent(self, user_input: str):
        prompt = SUB_AGENT_PROMPT.format(
            role=self.role,
            traits=", ".join(self.traits),
            user_input=user_input
        )
        return await self.inference(message=prompt, role="system")

    async def process_user_message(self, user_message: str):
        response = await self.inference(message=f'User added a take: {user_message}')
        print(f'Agent {self.name}: {response}')
        return response

    async def process_notification(self, notification: str):
        response = await self.inference(
            message=f'Message from the orchestrator: {notification}')
        return response
    
    


class Orchestrator:
    def __init__(self, agents: list[Agent], conversation_stacks: dict[str, list[str]] = None, previous_author_index: int = -1):
        self.messages = []
        self.llm = ChatOpenAI(model="gpt-5-mini")
        self.agents = agents
        self.conversation_stacks = conversation_stacks if conversation_stacks is not None else {agent.name: [] for agent in agents}
        self.is_user_speaking = False
        self.user_alias = "MainUser"
        self.previous_author_index = previous_author_index

    async def inference(self, message: str, role: str = "user"):
        self.messages.append({"role": role, "content": message})
        response = await self.llm.ainvoke(self.messages)
        self.messages.append(
            {"role": "assistant", "content": response.content})
        return response.content

    def initialize_orchestrator(self, user_input: str):
        agent_list = "\n".join(
            [f"Agent Name: {agent.name}, Role: {agent.role}, Traits: {', '.join(agent.traits)}" for agent in self.agents]
        )
        prompt = ORCHESTRATOR_PROMPT.format(
            agent_list=agent_list,
            user_input=user_input
        )
        self.messages.append({"role": "system", "content": prompt})

    async def process_agent_takes(self, agent_takes: dict):
        takes_message = "Here are the takes from the agents:\n"
        for agent_name, take in agent_takes.items():
            takes_message += f"Agent {agent_name} submitted the following take: {take}\n"
        return await self.inference(message=takes_message)

    async def send_notifications(self, notification: str):
        notification_response = {}

        async def send_to_agent(agent):
            response = await agent.process_notification(notification=notification)
            print(agent.name + f": {response}")
            return agent.name, response

        tasks = [send_to_agent(agent) for agent in self.agents]
        results = await asyncio.gather(*tasks)

        for agent_name, response in results:
            notification_response[agent_name] = response
        return notification_response

    def update_conversation_stack(self, agent_name: str, message: str):
        if agent_name in self.conversation_stacks:
            self.conversation_stacks[agent_name].append(message)
        else:
            raise ValueError(
                f"Agent {agent_name} not found in conversation stacks.")

    def clear_conversation_stack(self, agent_name: str):
        if agent_name in self.conversation_stacks:
            self.conversation_stacks[agent_name] = []
        else:
            raise ValueError(
                f"Agent {agent_name} not found in conversation stacks.")

    def update_conversation_stacks(self, previous_take: str, previous_take_author: str):
        if previous_take_author != self.user_alias:
            self.clear_conversation_stack(previous_take_author)
        for agent in self.agents:
            if agent.name != previous_take_author:
                self.update_conversation_stack(agent.name, f'{previous_take_author} says: {previous_take}')

    def update_conversation_stacks_bulk(self, agent_takes: dict):
        for agent_name, take in agent_takes.items():
            for agent in self.agents:
                if agent.name != agent_name:
                    self.update_conversation_stack(agent.name, take)

    async def decide_and_get_take(self):
        agent_index = random.randrange(start=0, stop=len(self.agents))
        if agent_index == self.previous_author_index:
            agent_index = (agent_index + 1) % len(self.agents)
        agent = self.agents[agent_index]
        response = await agent.inference(
            message=f"Here is the conversation stack for you: {self.conversation_stacks[agent.name]}, please provide your next take."
        )
        self.previous_author_index = agent_index
        return agent_index, response

    def check_user_interrupt(self):
        return keyboard.is_pressed('i')


async def main():
    store = RedisStore()
    store.create_session(
        session_id="session_123", agents=[
            AgentConfig(name="Agent1", role="Tech Expert", traits=["Innovative", "Analytical"], voice_id="6WjhCXzqp2hnSqFtrG8P"),
            AgentConfig(name="Agent2", role="Business Strategist", traits=["Pragmatic", "Visionary"], voice_id="rAsfH6d68tmh0XRGXp4D"),
            AgentConfig(name="Agent3", role="Marketing Guru", traits=["Creative", "Persuasive"], voice_id="xNtG3W2oqJs0cJZuTyBc"),
        ])
    
    async def run_discussion_loop(max_iterations: int = 100):
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            session_data = store.get_session("session_123")
            print(session_data)
            agents_state: list[AgentConfig] = session_data['agents_state']
            orchestrator_state: OrchestratorState = session_data['orchestrator_state']
            agents = [Agent(
                name=agent_cfg.name,
                role=agent_cfg.role,
                traits=agent_cfg.traits,
                voice_id=agent_cfg.voice_id,
                messages=agent_cfg.messages
            ) for agent_cfg in agents_state]
            orchestrator = Orchestrator(agents=agents, conversation_stacks=orchestrator_state.conversation_stacks, previous_author_index=orchestrator_state.previous_author_index)
            if iteration == 0:
                user_input = "count till 10 one by one"
                orchestrator.update_conversation_stacks(previous_take=user_input, previous_take_author=orchestrator.user_alias)
            agent_index, take = await orchestrator.decide_and_get_take()
            orchestrator.update_conversation_stacks(
            previous_take=take, previous_take_author=orchestrator.agents[agent_index].name)
            
            # print(
            #     # f"{orchestrator.agents[agent_index].name} provided take: {take}")
            syn(text=take, voice_id=orchestrator.agents[agent_index].voice_id)

            if orchestrator.check_user_interrupt():
                orchestrator.is_user_speaking = True
                user_take = input("User, please provide your take: ")
                orchestrator.update_conversation_stacks(
                    previous_take=user_take, previous_take_author=orchestrator.user_alias)
                orchestrator.is_user_speaking = False

            store.update_session(
                session_id="session_123",
                agents=[AgentConfig(name=agent.name, role=agent.role, traits=agent.traits, voice_id=agent.voice_id, messages=agent.messages) for agent in orchestrator.agents],
                orchestrator_state=OrchestratorState(
                    conversation_stacks=orchestrator.conversation_stacks,
                    previous_author_index=orchestrator.previous_author_index
                )
            )
    await run_discussion_loop()

asyncio.run(main())

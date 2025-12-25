import random
from services.prompts import SUB_AGENT_PROMPT, ORCHESTRATOR_PROMPT
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
import keyboard
load_dotenv()


class Agent:
    def __init__(self, name: str, role: str, traits: list = None):
        self.name = name
        self.role = role
        self.traits = traits if traits is not None else []
        self.messages = []
        self.llm = ChatOpenAI(model="gpt-5-mini")

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
    def __init__(self, agents: list[Agent]):
        self.messages = []
        self.llm = ChatOpenAI(model="gpt-5-mini")
        self.agents = agents
        self.conversation_stacks = {agent.name: [] for agent in agents}
        self.is_user_speaking = False
        self.user_alias = "MainUser"

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
            raise ValueError(f"Agent {agent_name} not found in conversation stacks.")
    
    def clear_conversation_stack(self, agent_name: str):
        if agent_name in self.conversation_stacks:
            self.conversation_stacks[agent_name] = []
        else:
            raise ValueError(f"Agent {agent_name} not found in conversation stacks.")

    def update_conversation_stacks(self, previous_take: str, previous_take_author: str):
        if previous_take_author != self.user_alias:
            self.clear_conversation_stack(previous_take_author)
        for agent in self.agents:
            if agent.name != previous_take_author:
                self.update_conversation_stack(agent.name, previous_take)
    
    def update_conversation_stacks_bulk(self, agent_takes: dict):
        for agent_name, take in agent_takes.items():
            for agent in self.agents:
                if agent.name != agent_name:
                    self.update_conversation_stack(agent.name, take)
    
    async def decide_and_get_take(self, prev_author_index: int):
        agent_index = random.randrange(start=0, stop=len(self.agents))
        if agent_index == prev_author_index:
            agent_index = (agent_index + 1) % len(self.agents)
        agent = self.agents[agent_index]
        response = await agent.inference(
            message=f"Here is the conversation stack for you: {self.conversation_stacks[agent.name]}, please provide your next take or if you are done, respond with 'IM DONE'."
        )
        self.update_conversation_stacks(previous_take=response, previous_take_author=agent.name)
        return agent_index, response

    def check_user_interrupt(self):
        return keyboard.is_pressed('i')

async def main():
    agent1 = Agent(name="Alex", role="Your thoughtful friend",
                   traits=["Empathetic", "Good listener", "Laid-back"])
    print("Initialized Agent 1")
    agent2 = Agent(name="Jordan", role="Your adventurous buddy",
                   traits=["Spontaneous", "Funny", "Open-minded"])
    print("Initialized Agent 2")
    orchestrator = Orchestrator(agents=[agent1, agent2])
    print("Initialized Orchestrator")
    user_input = "Come up with a sofyware startup idea and once everything is discussed and no more iteration is required start responding with 'IM DONE'"
    orchestrator.initialize_orchestrator(user_input=user_input)
    print("Orchestrator prompt initialized")

    res1, res2 = await asyncio.gather(
        agent1.initialize_agent(user_input=user_input),
        agent2.initialize_agent(user_input=user_input)
    )    

    print(res1)
    print(res2)

    initial_takes = {
        agent1.name: res1,
        agent2.name: res2
    }

    orchestrator.update_conversation_stacks_bulk(initial_takes)
    
    async def run_discussion_loop(max_iterations: int = 100):
        prev_author_index = -1
        for iteration in range(max_iterations):

            print(f"\n--- Iteration {iteration + 1} ---")
            agent_index, take = await orchestrator.decide_and_get_take(prev_author_index)
            prev_author_index = agent_index
            print(f"Agent {orchestrator.agents[agent_index].name} provided take: {take}")

            
            if orchestrator.check_user_interrupt():
                orchestrator.is_user_speaking = True
                user_take = input("User, please provide your take: ")
                orchestrator.update_conversation_stacks(previous_take=user_take, previous_take_author=orchestrator.user_alias)
                orchestrator.is_user_speaking = False

    await run_discussion_loop()

asyncio.run(main())

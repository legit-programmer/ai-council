from services.prompts import SUB_AGENT_PROMPT, ORCHESTRATOR_PROMPT
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
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


async def main():
    agent1 = Agent(name="Alex", role="Your thoughtful friend",
                   traits=["Empathetic", "Good listener", "Laid-back"])
    print("Initialized Agent 1")
    agent2 = Agent(name="Jordan", role="Your adventurous buddy",
                   traits=["Spontaneous", "Funny", "Open-minded"])
    print("Initialized Agent 2")
    orchestrator = Orchestrator(agents=[agent1, agent2])
    print("Initialized Orchestrator")
    user_input = "wassup guys, how are you doing today?"
    orchestrator.initialize_orchestrator(user_input=user_input)
    print("Orchestrator prompt initialized")

    res1, res2 = await asyncio.gather(
        agent1.initialize_agent(user_input=user_input),
        agent2.initialize_agent(user_input=user_input)
    )
    print("Agent 1 initial take submitted")
    print("Agent 2 initial take submitted")

    agent_takes = {
        agent1.name: res1,
        agent2.name: res2
    }

    async def run_discussion_loop(max_iterations: int = 10):
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            print("Processing agent takes through orchestrator...")
            orchestrator_response = await orchestrator.process_agent_takes(
                agent_takes=agent_takes)
            # print(orchestrator_response)

            new_takes = await orchestrator.send_notifications(orchestrator_response)
            agent_takes.update(new_takes)

    await run_discussion_loop()

asyncio.run(main())

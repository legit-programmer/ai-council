

class Agent:
    def __init__(self, name: str, role: str, traits: list = None):
        self.name = name
        self.role = role
        self.traits = traits if traits is not None else []
        self.messages = []

    def get_take(self, other_takes:list) -> str:
        # gets the latest takes from other agents and user and decides whether to reply or not"""

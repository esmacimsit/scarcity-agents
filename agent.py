class Agent:
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.food = 5
        self.coin = 5
        self.reputation = 0

    def wealth(self) -> int:
        return self.food + self.coin
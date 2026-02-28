import random
from agent import Agent


class World:

    def __init__(self, n_agents: int = 10, seed: int = 42):
        random.seed(seed)
        self.timestep = 0
        self.agents = [Agent(i) for i in range(n_agents)]
        self.log = []

    def random_policy(self, agent):
        return random.choice(["gather", "work"])

    def step(self):
        for agent in self.agents:

            # Consumption
            agent.food -= 1
            if agent.food < 0:
                agent.food = 0

            if agent.food > 0:
                action = self.random_policy(agent)

                if action == "gather":
                    agent.food += 2
                elif action == "work":
                    agent.coin += 2
            else:
                action = "starving"

            self.log.append({
                "timestep": self.timestep,
                "agent_id": agent.id,
                "action": action,
                "food": agent.food,
                "coin": agent.coin,
                "wealth": agent.wealth()
            })

        self.timestep += 1
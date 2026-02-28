import random
import math
from agent import Agent


class World:

    def __init__(self, n_agents=10, seed=42):

        random.seed(seed)

        self.timestep = 0
        self.agents = [Agent(i) for i in range(n_agents)]
        self.log = []

        self.r = 0.03
        self.g = 0.02
        self.base_food_price = 1.0
        self.food_supply_cap = int(n_agents * 1.2)

        self.shock_prob = 0.02
        self.shock_duration = 10

    def alive_count(self):
        return len(self.agents)

    def scarcity_index(self):
        if self.alive_count() == 0:
            return 0
        starving = sum(1 for a in self.agents if a.food <= 0)
        return starving / self.alive_count()

    def food_price(self):
        return self.base_food_price * (1 + 3 * self.scarcity_index())

    def random_policy(self, agent):
        return random.choice(["gather", "work"])

    def capital_return(self, agent):
        if agent.coin > 0:
            agent.coin += int(agent.coin * self.r)

    def maybe_apply_shock(self, agent):
        if random.random() < self.shock_prob:
            agent.shock_until = self.timestep + self.shock_duration

    def step(self):

        if self.alive_count() == 0:
            return

        alive_agents = []
        total_food_produced = 0

        price = self.food_price()

        for agent in list(self.agents):

            self.maybe_apply_shock(agent)

            self.capital_return(agent)

            agent.food -= 1

            if agent.food <= 0:
                if agent.coin >= price:
                    agent.coin -= int(price)
                    agent.food += 1
                else:
                    self.log.append({
                        "timestep": self.timestep,
                        "agent_id": agent.id,
                        "action": "dead",
                        "food": agent.food,
                        "coin": agent.coin,
                        "wealth": agent.wealth()
                    })
                    continue

            action = self.random_policy(agent)

            prod = agent.productivity(self.timestep)

            if action == "gather":
                if total_food_produced < self.food_supply_cap:
                    gain = int(2 * prod)
                    agent.food += gain
                    total_food_produced += gain
            else:
                gain = int(2 * prod * (1 + self.g))
                agent.coin += gain

            self.log.append({
                "timestep": self.timestep,
                "agent_id": agent.id,
                "action": action,
                "food": agent.food,
                "coin": agent.coin,
                "wealth": agent.wealth(),
                "price": price
            })

            alive_agents.append(agent)

        self.agents = alive_agents
        self.timestep += 1
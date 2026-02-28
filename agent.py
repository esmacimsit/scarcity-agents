import random

class Agent:

    def __init__(self, id):
        self.id = id
        self.food = 5
        self.coin = 5
        self.base_productivity = random.uniform(0.9, 1.1)

        self.shock_until = -1

    def wealth(self):
        return self.food + self.coin

    def productivity(self, timestep):
        if timestep < self.shock_until:
            return self.base_productivity * 0.5
        return self.base_productivity
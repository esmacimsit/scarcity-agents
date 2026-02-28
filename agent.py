import random

class Agent:

    def __init__(self, id):
        self.id = id
        self.food = 5
        self.coin = 5
        self.productivity = random.uniform(0.6, 1.4)

    def wealth(self, food_price):
        return self.coin + self.food * food_price
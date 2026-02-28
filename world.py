import random


class World:
    def __init__(self, n_agents: int = 50, seed: int = 42):
        random.seed(seed)

        self.timestep = 0
        self.initial_population = n_agents
        self.dead_count = 0

        self.agents = []
        for i in range(n_agents):
            self.agents.append({
                "id": i,
                "food": 5.0,
                "coin": 5.0,
                "productivity": random.uniform(0.8, 1.2)
            })

        self.log = []

        # --- Price system ---
        self.base_price = 2.0
        self.food_price = self.base_price
        self.price_alpha = 1.2
        self.price_min = 0.5
        self.price_max = 10.0
        self.ideal_food_per_agent = 6.0

        # --- Production bounds ---
        self.food_cap = 25.0
        self.coin_cap = 60.0
        self.base_gain = 3.0

        # --- Market rules ---
        self.reserve_food = 3.0
        self.sell_min = 4.0
        self.trade_limit_ratio = 0.5

    # ------------------------------
    # Core economics
    # ------------------------------

    def wealth(self, agent):
        return agent["coin"] + agent["food"] * self.food_price

    def update_price(self):
        total_food = sum(a["food"] for a in self.agents)
        alive = max(len(self.agents), 1)

        ideal_total = alive * self.ideal_food_per_agent
        scarcity_ratio = ideal_total / max(total_food, 1e-6)

        price = self.base_price * (scarcity_ratio ** self.price_alpha)
        self.food_price = max(self.price_min, min(self.price_max, price))

    def bounded_gain(self, current, cap, raw_gain):
        factor = 1.0 - min(max(current / cap, 0.0), 1.0)
        return max(0.0, raw_gain * factor)

    # ------------------------------
    # Policy
    # ------------------------------

    def random_policy(self):
        return random.choice(["gather", "work"])

    # ------------------------------
    # Trade
    # ------------------------------

    def try_buy_food(self, buyer):
        if buyer["coin"] < self.food_price:
            return False

        sellers = [
            a for a in self.agents
            if a["id"] != buyer["id"]
            and a["food"] >= self.sell_min
            and a["food"] > self.reserve_food
        ]

        if not sellers:
            return False

        seller = random.choice(sellers)

        buyer["coin"] -= self.food_price
        buyer["food"] += 1.0

        seller["coin"] += self.food_price
        seller["food"] -= 1.0

        return True

    # ------------------------------
    # Step
    # ------------------------------

    def step(self):
        # (a) consumption
        for a in self.agents:
            a["food"] = max(0.0, a["food"] - 1.0)

        # (b) price update
        self.update_price()

        # (c) emergency trade + death
        survivors = []
        for a in self.agents:
            if a["food"] <= 0.0:
                if not self.try_buy_food(a):
                    self.dead_count += 1
                    self.log.append({
                        "timestep": self.timestep,
                        "agent_id": a["id"],
                        "action": "dead",
                        "food": 0.0,
                        "coin": round(a["coin"], 3),
                        "price": round(self.food_price, 4),
                        "wealth": 0.0
                    })
                    continue
            survivors.append(a)

        self.agents = survivors

        # (d) decision
        actions = {a["id"]: self.random_policy() for a in self.agents}

        # (e) production
        for a in self.agents:
            raw = self.base_gain * a["productivity"] + random.uniform(-0.3, 0.3)

            if actions[a["id"]] == "gather":
                gain = self.bounded_gain(a["food"], self.food_cap, raw)
                a["food"] += gain
            else:
                gain = self.bounded_gain(a["coin"], self.coin_cap, raw)
                a["coin"] += gain

        # (f) limited trade
        trade_limit = max(1, int(len(self.agents) * self.trade_limit_ratio))
        trades = 0

        buyers = [a for a in self.agents if a["food"] < 1.0]

        for b in buyers:
            if trades >= trade_limit:
                break
            if self.try_buy_food(b):
                trades += 1

        # (g) log
        for a in self.agents:
            self.log.append({
                "timestep": self.timestep,
                "agent_id": a["id"],
                "action": actions[a["id"]],
                "food": round(a["food"], 3),
                "coin": round(a["coin"], 3),
                "price": round(self.food_price, 4),
                "wealth": round(self.wealth(a), 3)
            })

        self.timestep += 1

    # ------------------------------
    # Metrics
    # ------------------------------

    def summary_metrics(self):
        from utils import gini
        import statistics

        alive = len(self.agents)

        survivor_wealth = [self.wealth(a) for a in self.agents]
        population_wealth = survivor_wealth + [0.0] * (self.initial_population - alive)

        return {
            "alive": alive,
            "dead_total": self.dead_count,
            "price": self.food_price,
            "gini_survivor": gini(survivor_wealth) if survivor_wealth else 0.0,
            "gini_population": gini(population_wealth) if population_wealth else 0.0,
            "min_wealth": min(survivor_wealth) if survivor_wealth else 0.0,
            "median_wealth": statistics.median(survivor_wealth) if survivor_wealth else 0.0,
            "max_wealth": max(survivor_wealth) if survivor_wealth else 0.0,
        }
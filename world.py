import random
import math


class World:
    def __init__(self, n_agents=50, seed=42, config=None, policy="random"):
        self.rng = random.Random(seed)

        # ---- Config ----
        default_config = {
            "base_price": 2.0,
            "price_alpha": 1.2,
            "price_min": 0.5,
            "price_max": 10.0,
            "ideal_food_per_agent": 6.0,
            "food_cap": 25.0,
            "coin_cap": 60.0,
            "base_gain": 3.0,
            "reserve_food": 3.0,
            "sell_min": 4.0,
            "trade_limit_ratio": 0.5,
        }

        self.cfg = {**default_config, **(config or {})}
        self.policy = policy

        self.timestep = 0
        self.initial_population = n_agents
        self.dead_count = 0

        self.agents = []
        for i in range(n_agents):
            self.agents.append({
                "id": i,
                "food": 5.0,
                "coin": 5.0,
                "productivity": self.rng.uniform(0.8, 1.2)
            })

        self.agent_log = []
        self.step_log = []

        self.food_price = self.cfg["base_price"]

    # --------------------
    # Core
    # --------------------

    def wealth(self, agent):
        return agent["coin"] + agent["food"] * self.food_price

    def update_price(self):
        total_food = sum(agent["food"] for agent in self.agents)
        alive = max(len(self.agents), 1)

        ideal_total = alive * self.cfg["ideal_food_per_agent"]
        scarcity_ratio = ideal_total / max(total_food, 1e-6)

        price = self.cfg["base_price"] * (scarcity_ratio ** self.cfg["price_alpha"])
        self.food_price = max(
            self.cfg["price_min"],
            min(self.cfg["price_max"], price)
        )

    def bounded_gain(self, current, cap, raw):
        factor = 1.0 - min(max(current / cap, 0.0), 1.0)
        return max(0.0, raw * factor)

    def build_decision_context(self, agent):
        """
        Builds a compact decision context for rule-based and future LLM policies.
        This keeps the input state stable across random, rule, LLM, and fine-tuned LLM experiments.
        """
        total_food = sum(a["food"] for a in self.agents)
        alive_count = len(self.agents)
        ideal_total = max(alive_count, 1) * self.cfg["ideal_food_per_agent"]
        scarcity_ratio = ideal_total / max(total_food, 1e-6)

        return {
            "timestep": self.timestep,
            "agent_id": agent["id"],
            "food": round(agent["food"], 3),
            "coin": round(agent["coin"], 3),
            "productivity": round(agent["productivity"], 3),
            "wealth": round(self.wealth(agent), 3),
            "food_price": round(self.food_price, 4),
            "alive_count": alive_count,
            "dead_total": self.dead_count,
            "total_food": round(total_food, 3),
            "scarcity_ratio": round(scarcity_ratio, 4),
        }

    def normalize_action(self, action):
        """
        Normalizes model or policy output into a valid simulator action.
        Invalid outputs safely fall back to gather, which is survival-oriented.
        """
        if action is None:
            return "gather"

        normalized = str(action).strip().lower()
        if normalized in {"gather", "work"}:
            return normalized

        return "gather"

    def decide_llm_action(self, agent, context):
        """
        Placeholder for future LLM-backed decision making.
        Later this method will call a model and return only: gather or work.
        """
        # Temporary fallback until LLM integration is implemented.
        return self.rng.choice(["gather", "work"])

    def decide_action(self, agent):
        """
        Selects an action for a single agent.

        Policies:
        - random: stochastic baseline
        - rule: deterministic non-LLM baseline
        - llm: placeholder for future LLM integration
        - finetuned_llm: placeholder for future fine-tuned LLM integration
        """
        context = self.build_decision_context(agent)

        if self.policy == "random":
            return self.normalize_action(self.rng.choice(["gather", "work"]))

        if self.policy == "rule":
            if context["food"] < 2.0:
                return "gather"

            if context["coin"] < context["food_price"]:
                return "work"

            if context["food_price"] > self.cfg["base_price"] * 1.5 and context["food"] < 5.0:
                return "gather"

            if context["food"] > 8.0 and context["coin"] < 10.0:
                return "work"

            return self.normalize_action(self.rng.choice(["gather", "work"]))

        if self.policy in {"llm", "finetuned_llm"}:
            return self.normalize_action(self.decide_llm_action(agent, context))

        raise ValueError(f"Unknown policy: {self.policy}")

    # --------------------
    # Trade
    # --------------------

    def try_buy_food(self, buyer):
        if buyer["coin"] < self.food_price:
            return False

        sellers = [
            agent for agent in self.agents
            if agent["id"] != buyer["id"]
            and agent["food"] >= self.cfg["sell_min"]
            and agent["food"] > self.cfg["reserve_food"]
        ]

        if not sellers:
            return False

        seller = self.rng.choice(sellers)

        buyer["coin"] -= self.food_price
        buyer["food"] += 1.0

        seller["coin"] += self.food_price
        seller["food"] -= 1.0

        return True

    # --------------------
    # Step
    # --------------------

    def step(self):
        deaths_this_step = 0
        trades = 0
        trade_limit = max(1, int(len(self.agents) * self.cfg["trade_limit_ratio"]))

        # (a) consumption
        for agent in self.agents:
            agent["food"] = max(0.0, agent["food"] - 1.0)

        # (b) price update
        self.update_price()

        # (c) emergency trade + death
        survivors = []
        for agent in self.agents:
            if agent["food"] <= 0.0:
                if trades < trade_limit and self.try_buy_food(agent):
                    trades += 1
                else:
                    self.dead_count += 1
                    deaths_this_step += 1
                    continue
            survivors.append(agent)

        self.agents = survivors

        # (d) decision
        actions = {}
        decision_contexts = {}
        for agent in self.agents:
            decision_contexts[agent["id"]] = self.build_decision_context(agent)
            actions[agent["id"]] = self.decide_action(agent)

        gather_count = sum(1 for action in actions.values() if action == "gather")
        work_count = sum(1 for action in actions.values() if action == "work")

        # (e) production
        for agent in self.agents:
            raw = self.cfg["base_gain"] * agent["productivity"] + self.rng.uniform(-0.3, 0.3)

            if actions[agent["id"]] == "gather":
                gain = self.bounded_gain(agent["food"], self.cfg["food_cap"], raw)
                agent["food"] += gain
            else:
                gain = self.bounded_gain(agent["coin"], self.cfg["coin_cap"], raw)
                agent["coin"] += gain

        # (f) normal trade
        buyers = [agent for agent in self.agents if agent["food"] < 1.0]

        for buyer in buyers:
            if trades >= trade_limit:
                break
            if self.try_buy_food(buyer):
                trades += 1

        # (g) invariants
        for agent in self.agents:
            assert agent["food"] >= 0
            assert agent["coin"] >= 0
            assert not math.isnan(agent["food"])
            assert not math.isnan(agent["coin"])

        # (h) logs
        total_food = sum(agent["food"] for agent in self.agents)
        total_coin = sum(agent["coin"] for agent in self.agents)

        from utils import gini
        survivor_wealth = [self.wealth(agent) for agent in self.agents]
        population_wealth = survivor_wealth + [0.0] * (self.initial_population - len(self.agents))

        gini_survivor = gini(survivor_wealth) if survivor_wealth else 0.0
        gini_population = gini(population_wealth) if population_wealth else 0.0

        self.step_log.append({
            "timestep": self.timestep,
            "policy": self.policy,
            "alive": len(self.agents),
            "dead_total": self.dead_count,
            "deaths_this_step": deaths_this_step,
            "total_food": round(total_food, 3),
            "total_coin": round(total_coin, 3),
            "price": round(self.food_price, 4),
            "trades": trades,
            "gather_count": gather_count,
            "work_count": work_count,
            "gini_survivor": round(gini_survivor, 4),
            "gini_population": round(gini_population, 4),
        })

        for agent in self.agents:
            self.agent_log.append({
                "timestep": self.timestep,
                "policy": self.policy,
                "agent_id": agent["id"],
                "food": round(agent["food"], 3),
                "coin": round(agent["coin"], 3),
                "productivity": round(agent["productivity"], 3),
                "wealth": round(self.wealth(agent), 3),
                "price": round(self.food_price, 4),
                "scarcity_ratio": decision_contexts[agent["id"]]["scarcity_ratio"],
                "alive_count": decision_contexts[agent["id"]]["alive_count"],
                "action": actions.get(agent["id"], "none"),
                "alive": True,
            })

        self.timestep += 1
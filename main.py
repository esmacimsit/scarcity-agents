from world import World
from utils import gini
import csv


def run_simulation():
    world = World(n_agents=50, seed=42)

    TIMESTEPS = 300

    for _ in range(TIMESTEPS):
        world.step()

    if len(world.log) > 0:
        with open("simulation_log.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=world.log[0].keys())
            writer.writeheader()
            writer.writerows(world.log)

    final_wealth = [agent.wealth() for agent in world.agents]

    print("Alive:", len(world.agents))
    print("Final Wealth:", final_wealth)
    print("Gini:", round(gini(final_wealth), 3))


if __name__ == "__main__":
    run_simulation()
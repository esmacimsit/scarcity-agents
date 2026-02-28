from world import World
import csv


def run_simulation(n_agents=50, timesteps=300, seed=42):
    world = World(n_agents=n_agents, seed=seed)

    for _ in range(timesteps):
        world.step()

    if world.log:
        with open("simulation_log.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=world.log[0].keys())
            writer.writeheader()
            writer.writerows(world.log)

    m = world.summary_metrics()

    print("\n===== FINAL SUMMARY =====")
    print("Alive:", m["alive"])
    print("Total Dead:", m["dead_total"])
    print("Final Price:", round(m["price"], 4))
    print("Gini (Survivors):", round(m["gini_survivor"], 4))
    print("Gini (Population):", round(m["gini_population"], 4))
    print(
        "Min / Median / Max Wealth:",
        round(m["min_wealth"], 2),
        round(m["median_wealth"], 2),
        round(m["max_wealth"], 2),
    )


if __name__ == "__main__":
    run_simulation()
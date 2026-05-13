from world import World
import csv
import os


def run_simulation(n_agents=50, timesteps=300, seed=42, policy="random", scenario="default", config=None, output_dir="logs"):
    world = World(n_agents=n_agents, seed=seed, policy=policy, config=config)
    os.makedirs(output_dir, exist_ok=True)

    for _ in range(timesteps):
        world.step()

    # Step-level log
    step_log_path = os.path.join(output_dir, f"{scenario}_{policy}_seed_{seed}_step_log.csv")
    if world.step_log:
        with open(step_log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=world.step_log[0].keys())
            writer.writeheader()
            writer.writerows(world.step_log)

    # Agent-level log
    agent_log_path = os.path.join(output_dir, f"{scenario}_{policy}_seed_{seed}_agent_log.csv")
    if world.agent_log:
        with open(agent_log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=world.agent_log[0].keys())
            writer.writeheader()
            writer.writerows(world.agent_log)

    if not world.step_log:
        print("No simulation steps were executed.")
        return world

    final = world.step_log[-1]

    print("\n===== FINAL SUMMARY =====")
    print("Scenario:", scenario)
    print("Policy:", final["policy"])
    print("Seed:", seed)
    print("Alive:", final["alive"])
    print("Total Dead:", final["dead_total"])
    print("Final Price:", final["price"])
    print("Gather Count:", final["gather_count"])
    print("Work Count:", final["work_count"])
    print("Gini (Survivors):", final["gini_survivor"])
    print("Gini (Population):", final["gini_population"])
    print("Step Log:", step_log_path)
    print("Agent Log:", agent_log_path)

    return world


def run_experiments(policies=("random", "rule"), seeds=(1, 2, 3, 4, 5), n_agents=50, timesteps=300):
    scenarios = {
        "default": None,
        "scarcity": {
            "base_gain": 1.7,
            "ideal_food_per_agent": 7.0,
            "trade_limit_ratio": 0.3,
        },
    }

    for scenario, config in scenarios.items():
        for policy in policies:
            for seed in seeds:
                run_simulation(
                    n_agents=n_agents,
                    timesteps=timesteps,
                    seed=seed,
                    policy=policy,
                    scenario=scenario,
                    config=config,
                )


if __name__ == "__main__":
    run_experiments()
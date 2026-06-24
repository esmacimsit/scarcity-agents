from world import World
import argparse
import csv
import os


POLICY_SETS = {
    "baseline": ("random", "rule"),
    "zero-shot": (
        "llm_survival",
        "llm_social_welfare",
        "llm_wealth_maximizing",
    ),
    "few-shot": (
        "llm_survival_few_shot",
        "llm_social_welfare_few_shot",
        "llm_wealth_maximizing_few_shot",
    ),
    "all": (
        "random",
        "rule",
        "llm_survival",
        "llm_social_welfare",
        "llm_wealth_maximizing",
        "llm_survival_few_shot",
        "llm_social_welfare_few_shot",
        "llm_wealth_maximizing_few_shot",
    ),
}

DEFAULT_POLICY_SET = "baseline"

SCENARIOS = {
    "default": None,
    "moderate_scarcity": {
        "base_gain": 2.2,
        "ideal_food_per_agent": 6.5,
        "trade_limit_ratio": 0.4,
    },
    "scarcity": {
        "base_gain": 1.7,
        "ideal_food_per_agent": 7.0,
        "trade_limit_ratio": 0.3,
    },
}


def run_simulation(
    n_agents=50,
    timesteps=300,
    seed=42,
    policy="random",
    scenario="default",
    config=None,
    output_dir="logs",
):
    world = World(n_agents=n_agents, seed=seed, policy=policy, config=config)
    os.makedirs(output_dir, exist_ok=True)

    for _ in range(timesteps):
        world.step()

    step_log_path = os.path.join(
        output_dir,
        f"{scenario}_{policy}_seed_{seed}_step_log.csv",
    )
    if world.step_log:
        with open(step_log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=world.step_log[0].keys())
            writer.writeheader()
            writer.writerows(world.step_log)

    agent_log_path = os.path.join(
        output_dir,
        f"{scenario}_{policy}_seed_{seed}_agent_log.csv",
    )
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


def run_experiments(
    policies=None,
    seeds=(1, 2, 3, 4, 5),
    n_agents=50,
    timesteps=300,
    scenarios=None,
):
    if policies is None:
        policies = POLICY_SETS[DEFAULT_POLICY_SET]

    if scenarios is None:
        selected_scenarios = SCENARIOS.items()
    else:
        unknown_scenarios = [scenario for scenario in scenarios if scenario not in SCENARIOS]
        if unknown_scenarios:
            valid_scenarios = ", ".join(SCENARIOS.keys())
            raise ValueError(
                "Unknown scenario(s): "
                f"{', '.join(unknown_scenarios)}. "
                f"Valid scenarios: {valid_scenarios}"
            )
        selected_scenarios = ((scenario, SCENARIOS[scenario]) for scenario in scenarios)

    for scenario, config in selected_scenarios:
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AI society simulation experiments."
    )
    parser.add_argument(
        "--policy-set",
        choices=sorted(POLICY_SETS.keys()),
        default=DEFAULT_POLICY_SET,
        help="Predefined policy set to run.",
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        default=None,
        help="Optional explicit policy list. Overrides --policy-set.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=[1, 2, 3, 4, 5],
        help="Seed values to run.",
    )
    parser.add_argument(
        "--n-agents",
        type=int,
        default=50,
        help="Number of agents in each simulation run.",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=300,
        help="Number of timesteps per simulation run.",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=sorted(SCENARIOS.keys()),
        default=None,
        help="Optional scenario list to run. Defaults to all scenarios.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    selected_policies = args.policies or POLICY_SETS[args.policy_set]

    print("Selected policy set:", args.policy_set)
    print("Selected policies:", ", ".join(selected_policies))
    print("Seeds:", args.seeds)
    print("Agents:", args.n_agents)
    print("Timesteps:", args.timesteps)
    if args.scenarios is not None:
        print("Scenarios:", ", ".join(args.scenarios))

    run_experiments(
        policies=tuple(selected_policies),
        seeds=tuple(args.seeds),
        n_agents=args.n_agents,
        timesteps=args.timesteps,
        scenarios=None if args.scenarios is None else tuple(args.scenarios),
    )

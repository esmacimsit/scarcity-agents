import csv
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from world import World


MODERATE_SCARCITY_CONFIG = {
    "base_gain": 2.2,
    "ideal_food_per_agent": 6.5,
    "trade_limit_ratio": 0.4,
}


ZERO_SHOT_POLICIES = [
    "llm_survival",
    "llm_social_welfare",
    "llm_wealth_maximizing",
]


OUTPUT_PATH = os.path.join(PROJECT_ROOT, "logs", "smoke_zero_shot_summary.csv")


def run_policy_smoke_test(policy):
    world = World(
        n_agents=5,
        seed=1,
        policy=policy,
        config=MODERATE_SCARCITY_CONFIG,
    )

    for _ in range(10):
        world.step()

    final = world.step_log[-1]

    total_gather = sum(row["gather_count"] for row in world.step_log)
    total_work = sum(row["work_count"] for row in world.step_log)
    total_actions = total_gather + total_work

    gather_ratio = round(total_gather / total_actions, 4) if total_actions else 0.0
    work_ratio = round(total_work / total_actions, 4) if total_actions else 0.0

    return {
        "policy": policy,
        "scenario": "moderate_scarcity",
        "seed": 1,
        "n_agents": 5,
        "timesteps": 10,
        "alive": final["alive"],
        "dead_total": final["dead_total"],
        "final_price": final["price"],
        "final_gini_population": final["gini_population"],
        "final_gather_count": final["gather_count"],
        "final_work_count": final["work_count"],
        "total_gather": total_gather,
        "total_work": total_work,
        "gather_ratio": gather_ratio,
        "work_ratio": work_ratio,
        "last_5_steps": world.step_log[-5:],
    }


def print_result(result):
    print("=" * 80)
    print("Policy:", result["policy"])
    print("Alive:", result["alive"])
    print("Dead total:", result["dead_total"])
    print("Final price:", result["final_price"])
    print("Gather count final step:", result["final_gather_count"])
    print("Work count final step:", result["final_work_count"])
    print("Gini population:", result["final_gini_population"])
    print("Total gather:", result["total_gather"])
    print("Total work:", result["total_work"])
    print("Gather ratio:", result["gather_ratio"])
    print("Work ratio:", result["work_ratio"])

    print("Last 5 steps:")
    for row in result["last_5_steps"]:
        print(
            "t=", row["timestep"],
            "alive=", row["alive"],
            "price=", row["price"],
            "gather=", row["gather_count"],
            "work=", row["work_count"],
            "dead=", row["dead_total"],
        )


def write_summary_csv(results):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    fieldnames = [
        "policy",
        "scenario",
        "seed",
        "n_agents",
        "timesteps",
        "alive",
        "dead_total",
        "final_price",
        "final_gini_population",
        "final_gather_count",
        "final_work_count",
        "total_gather",
        "total_work",
        "gather_ratio",
        "work_ratio",
    ]

    with open(OUTPUT_PATH, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {key: result[key] for key in fieldnames}
            writer.writerow(row)

    print("=" * 80)
    print("Wrote smoke test summary to:", OUTPUT_PATH)


def run_smoke_test():
    results = []

    for policy in ZERO_SHOT_POLICIES:
        result = run_policy_smoke_test(policy)
        results.append(result)
        print_result(result)

    write_summary_csv(results)


if __name__ == "__main__":
    run_smoke_test()
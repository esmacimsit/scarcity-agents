import argparse
import csv
import os
import statistics
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
OUTPUT_PATH = PROJECT_ROOT / "experiment_summary.csv"


def parse_policy_and_seed(file_path):
    """
    Expected filename formats:
    random_seed_1_step_log.csv
    rule_seed_5_step_log.csv
    default_random_seed_1_step_log.csv
    scarcity_rule_seed_5_step_log.csv
    """
    filename = file_path.name

    if not filename.endswith("_step_log.csv"):
        raise ValueError(f"Not a step log file: {filename}")

    stem = filename.replace("_step_log.csv", "")
    parts = stem.split("_seed_")

    if len(parts) != 2:
        raise ValueError(f"Unexpected filename format: {filename}")

    left_side = parts[0]
    seed = int(parts[1])

    known_policies = {
        "random",
        "rule",
        "llm_survival",
        "llm_social_welfare",
        "llm_wealth_maximizing",
        "llm_survival_few_shot",
        "llm_social_welfare_few_shot",
        "llm_wealth_maximizing_few_shot",
    }

    policy = None
    scenario = None

    for candidate_policy in sorted(known_policies, key=len, reverse=True):
        if left_side == candidate_policy:
            policy = candidate_policy
            scenario = "default"
            break

        suffix = f"_{candidate_policy}"
        if left_side.endswith(suffix):
            policy = candidate_policy
            scenario = left_side[: -len(suffix)] or "default"
            break

    if policy is None:
        policy = left_side
        scenario = "default"

    return scenario, policy, seed


def read_csv_rows(file_path):
    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def mean(values):
    values = list(values)
    if not values:
        return 0.0
    return statistics.mean(values)


def stdev(values):
    values = list(values)
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def summarize_step_log(file_path):
    scenario, policy, seed = parse_policy_and_seed(file_path)
    rows = read_csv_rows(file_path)

    if not rows:
        return None

    final = rows[-1]

    prices = [to_float(row.get("price")) for row in rows]
    gather_counts = [to_float(row.get("gather_count")) for row in rows]
    work_counts = [to_float(row.get("work_count")) for row in rows]
    trades = [to_float(row.get("trades")) for row in rows]
    deaths_this_step = [to_float(row.get("deaths_this_step")) for row in rows]

    final_alive = to_int(final.get("alive"))
    total_dead = to_int(final.get("dead_total"))

    initial_population = final_alive + total_dead
    survival_rate = final_alive / initial_population if initial_population > 0 else 0.0

    total_actions = sum(gather_counts) + sum(work_counts)
    gather_ratio = sum(gather_counts) / total_actions if total_actions > 0 else 0.0
    work_ratio = sum(work_counts) / total_actions if total_actions > 0 else 0.0

    return {
        "scenario": scenario,
        "policy": policy,
        "seed": seed,
        "timesteps": len(rows),
        "initial_population": initial_population,
        "final_alive": final_alive,
        "total_dead": total_dead,
        "survival_rate": round(survival_rate, 4),
        "final_price": round(to_float(final.get("price")), 4),
        "avg_price": round(mean(prices), 4),
        "price_volatility": round(stdev(prices), 4),
        "final_gini_survivor": round(to_float(final.get("gini_survivor")), 4),
        "final_gini_population": round(to_float(final.get("gini_population")), 4),
        "avg_gather_count": round(mean(gather_counts), 4),
        "avg_work_count": round(mean(work_counts), 4),
        "gather_ratio": round(gather_ratio, 4),
        "work_ratio": round(work_ratio, 4),
        "avg_trades": round(mean(trades), 4),
        "total_deaths_from_steps": round(sum(deaths_this_step), 4),
    }


def collect_summaries(log_dir=LOG_DIR):
    log_dir = Path(log_dir)

    if not log_dir.exists():
        raise FileNotFoundError(
            f"Log directory not found: {log_dir}. Run `python main.py` first."
        )

    summaries = []

    for file_path in sorted(log_dir.glob("*_step_log.csv")):
        summary = summarize_step_log(file_path)
        if summary is not None:
            summaries.append(summary)

    return summaries


def write_summary_csv(summaries):
    if not summaries:
        print("No step log files found. Run `python main.py` first.")
        return

    fieldnames = list(summaries[0].keys())

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)

    print(f"Wrote experiment summary to: {OUTPUT_PATH}")


def print_policy_averages(summaries):
    grouped = {}

    for row in summaries:
        key = (row["scenario"], row["policy"])
        grouped.setdefault(key, []).append(row)

    print("\n===== SCENARIO / POLICY AVERAGES =====")

    for (scenario, policy), rows in sorted(grouped.items()):
        avg_survival = mean(row["survival_rate"] for row in rows)
        avg_dead = mean(row["total_dead"] for row in rows)
        avg_price = mean(row["avg_price"] for row in rows)
        avg_gini_population = mean(row["final_gini_population"] for row in rows)
        avg_gather_ratio = mean(row["gather_ratio"] for row in rows)

        print(f"\nScenario: {scenario}")
        print(f"Policy: {policy}")
        print(f"Runs: {len(rows)}")
        print(f"Average survival rate: {avg_survival:.4f}")
        print(f"Average total dead: {avg_dead:.2f}")
        print(f"Average price: {avg_price:.4f}")
        print(f"Average final population Gini: {avg_gini_population:.4f}")
        print(f"Average gather ratio: {avg_gather_ratio:.4f}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize AI society experiment step logs."
    )
    parser.add_argument(
        "--log-dir",
        default=str(LOG_DIR),
        help="Directory containing *_step_log.csv files.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    summaries = collect_summaries(log_dir=args.log_dir)
    write_summary_csv(summaries)
    print_policy_averages(summaries)


if __name__ == "__main__":
    main()
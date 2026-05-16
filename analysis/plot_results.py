import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
FIGURE_DIR = PROJECT_ROOT / "analysis" / "figures"


def parse_step_log_filename(file_path):
    """
    Expected filename format:
    default_random_seed_1_step_log.csv
    moderate_scarcity_rule_seed_5_step_log.csv
    scarcity_random_seed_3_step_log.csv
    """
    filename = file_path.name

    if not filename.endswith("_step_log.csv"):
        raise ValueError(f"Not a step log file: {filename}")

    stem = filename.replace("_step_log.csv", "")
    left_side, seed_text = stem.rsplit("_seed_", 1)
    seed = int(seed_text)

    known_policies = {
        "random",
        "rule",
        "llm_survival",
        "llm_social_welfare",
        "llm_wealth_maximizing",
        "llm_survival_few_shot",
        "llm_social_welfare_few_shot",
        "llm_wealth_maximizing_few_shot",
        "finetuned_survival",
        "finetuned_social_welfare",
        "finetuned_wealth_maximizing",
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
        raise ValueError(f"Could not parse policy from filename: {filename}")

    return scenario, policy, seed


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def read_step_log(file_path):
    scenario, policy, seed = parse_step_log_filename(file_path)

    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    parsed_rows = []
    for row in rows:
        alive = to_float(row.get("alive"))
        gather_count = to_float(row.get("gather_count"))
        work_count = to_float(row.get("work_count"))
        total_actions = gather_count + work_count

        if alive > 0 and total_actions > 0:
            gather_ratio = gather_count / total_actions
        else:
            gather_ratio = None

        if alive > 0:
            gini_population = to_float(row.get("gini_population"))
        else:
            gini_population = None

        parsed_rows.append({
            "scenario": scenario,
            "policy": policy,
            "seed": seed,
            "timestep": int(to_float(row.get("timestep"))),
            "alive": alive,
            "price": to_float(row.get("price")),
            "gini_population": gini_population,
            "gather_ratio": gather_ratio,
        })

    return parsed_rows


def load_all_step_logs(log_dir=LOG_DIR):
    log_dir = Path(log_dir)

    if not log_dir.exists():
        raise FileNotFoundError(
            f"Log directory not found: {log_dir}. Run `python main.py` first."
        )

    all_rows = []
    for file_path in sorted(log_dir.glob("*_step_log.csv")):
        all_rows.extend(read_step_log(file_path))

    if not all_rows:
        raise FileNotFoundError(
            f"No step log files found in {log_dir}. Run `python main.py` first."
        )

    return all_rows


def mean(values):
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / len(values)


def average_by_timestep(rows, metric):
    grouped = defaultdict(list)

    for row in rows:
        key = (row["scenario"], row["policy"], row["timestep"])
        grouped[key].append(row[metric])

    averaged = defaultdict(list)

    for (scenario, policy, timestep), values in grouped.items():
        metric_mean = mean(values)
        if metric_mean is None:
            continue

        averaged[(scenario, policy)].append({
            "timestep": timestep,
            metric: metric_mean,
        })

    for key in averaged:
        averaged[key] = sorted(averaged[key], key=lambda item: item["timestep"])

    return averaged


def get_scenarios(rows):
    """
    Returns sorted scenario names found in the loaded step logs.
    """
    return sorted({row["scenario"] for row in rows})


def plot_metric(rows, metric, ylabel, title, output_filename, scenario_filter=None):
    if scenario_filter is not None:
        rows = [row for row in rows if row["scenario"] == scenario_filter]

    averaged = average_by_timestep(rows, metric)

    plt.figure(figsize=(11, 6))

    for (scenario, policy), series in sorted(averaged.items()):
        timesteps = [item["timestep"] for item in series]
        values = [item[metric] for item in series]
        label = policy if scenario_filter is not None else f"{scenario} / {policy}"
        plt.plot(timesteps, values, label=label)

    plot_title = title
    if scenario_filter is not None:
        plot_title = f"{title} ({scenario_filter})"

    plt.title(plot_title)
    plt.xlabel("Timestep")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()

    output_path = FIGURE_DIR / output_filename
    plt.savefig(output_path, dpi=160)
    plt.close()

    print(f"Saved figure: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot AI society experiment step logs."
    )
    parser.add_argument(
        "--log-dir",
        default=str(LOG_DIR),
        help="Directory containing *_step_log.csv files.",
    )
    parser.add_argument(
        "--split-by-scenario",
        action="store_true",
        help="Generate one set of figures per scenario instead of one combined figure.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(FIGURE_DIR),
        help="Directory where generated figures will be written.",
    )
    return parser.parse_args()


def plot_all_metrics(rows, output_suffix="", scenario_filter=None):
    suffix = f"_{output_suffix}" if output_suffix else ""

    plot_metric(
        rows=rows,
        metric="alive",
        ylabel="Alive Agents",
        title="Alive Agents Over Time",
        output_filename=f"alive_over_time{suffix}.png",
        scenario_filter=scenario_filter,
    )

    plot_metric(
        rows=rows,
        metric="price",
        ylabel="Food Price",
        title="Food Price Over Time",
        output_filename=f"price_over_time{suffix}.png",
        scenario_filter=scenario_filter,
    )

    plot_metric(
        rows=rows,
        metric="gini_population",
        ylabel="Population Gini",
        title="Population Gini Over Time",
        output_filename=f"gini_population_over_time{suffix}.png",
        scenario_filter=scenario_filter,
    )

    plot_metric(
        rows=rows,
        metric="gather_ratio",
        ylabel="Gather Ratio",
        title="Gather Ratio Over Time",
        output_filename=f"gather_ratio_over_time{suffix}.png",
        scenario_filter=scenario_filter,
    )


def main():
    args = parse_args()
    global FIGURE_DIR
    FIGURE_DIR = Path(args.output_dir)
    if not FIGURE_DIR.is_absolute():
        FIGURE_DIR = PROJECT_ROOT / FIGURE_DIR
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_all_step_logs(log_dir=args.log_dir)

    if args.split_by_scenario:
        for scenario in get_scenarios(rows):
            plot_all_metrics(
                rows=rows,
                output_suffix=scenario,
                scenario_filter=scenario,
            )
    else:
        plot_all_metrics(rows=rows)


if __name__ == "__main__":
    main()
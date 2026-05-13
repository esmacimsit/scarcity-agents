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

    known_policies = {"random", "rule", "llm", "finetuned_llm"}
    left_parts = left_side.split("_")

    if left_parts[-1] not in known_policies:
        raise ValueError(f"Could not parse policy from filename: {filename}")

    policy = left_parts[-1]
    scenario = "_".join(left_parts[:-1])

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


def load_all_step_logs():
    if not LOG_DIR.exists():
        raise FileNotFoundError(
            f"Log directory not found: {LOG_DIR}. Run `python main.py` first."
        )

    all_rows = []
    for file_path in sorted(LOG_DIR.glob("*_step_log.csv")):
        all_rows.extend(read_step_log(file_path))

    if not all_rows:
        raise FileNotFoundError(
            f"No step log files found in {LOG_DIR}. Run `python main.py` first."
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


def plot_metric(rows, metric, ylabel, title, output_filename):
    averaged = average_by_timestep(rows, metric)

    plt.figure(figsize=(11, 6))

    for (scenario, policy), series in sorted(averaged.items()):
        timesteps = [item["timestep"] for item in series]
        values = [item[metric] for item in series]
        label = f"{scenario} / {policy}"
        plt.plot(timesteps, values, label=label)

    plt.title(title)
    plt.xlabel("Timestep")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()

    output_path = FIGURE_DIR / output_filename
    plt.savefig(output_path, dpi=160)
    plt.close()

    print(f"Saved figure: {output_path}")


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_all_step_logs()

    plot_metric(
        rows=rows,
        metric="alive",
        ylabel="Alive Agents",
        title="Alive Agents Over Time",
        output_filename="alive_over_time.png",
    )

    plot_metric(
        rows=rows,
        metric="price",
        ylabel="Food Price",
        title="Food Price Over Time",
        output_filename="price_over_time.png",
    )

    plot_metric(
        rows=rows,
        metric="gini_population",
        ylabel="Population Gini",
        title="Population Gini Over Time",
        output_filename="gini_population_over_time.png",
    )

    plot_metric(
        rows=rows,
        metric="gather_ratio",
        ylabel="Gather Ratio",
        title="Gather Ratio Over Time",
        output_filename="gather_ratio_over_time.png",
    )


if __name__ == "__main__":
    main()
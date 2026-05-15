#!/usr/bin/env python3
"""
Validate teacher-guided fine-tune datasets for the AI Society project.

This script reads accepted/rejected JSONL files under data/finetune/<regime>/
and reports:
- accepted/rejected counts
- gather/work action distribution
- rejection reasons
- food/scarcity/price bucket coverage
- duplicate and conflict checks
- strict regime-specific validation thresholds

It writes a Markdown report to analysis/finetune_dataset_report.md by default.
It does not call the teacher API and does not consume inference credits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "finetune"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "analysis" / "finetune_dataset_report.md"

REGIMES = ["survival", "social_welfare", "wealth_maximizing"]
ACTIONS = {"gather", "work"}

STRICT_THRESHOLDS = {
    "survival": {
        "min_gather_ratio": 0.35,
        "max_gather_ratio": 0.65,
        "critical_food_gather_ratio": 1.0,
    },
    "social_welfare": {
        "min_gather_ratio": 0.50,
        "high_scarcity_gather_ratio": 0.70,
        "critical_food_gather_ratio": 1.0,
    },
    "wealth_maximizing": {
        "min_work_ratio": 0.70,
        "critical_food_gather_ratio": 1.0,
        "min_gather_ratio": 0.05,
    },
}


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_number}: {exc}") from exc

    return rows


def get_state(row: dict[str, Any]) -> dict[str, Any]:
    state = row.get("state")
    if not isinstance(state, dict):
        return {}
    return state


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def percentage(part: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def ratio(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return part / total


# ---------------------------------------------------------------------------
# Buckets and duplicate signatures
# ---------------------------------------------------------------------------


def bucket_food(value: float | int | None) -> str:
    if value is None:
        return "missing"
    if value <= 2.0:
        return "critical_food_<=2"
    if value <= 4.0:
        return "low_food_2_4"
    if value <= 7.0:
        return "medium_food_4_7"
    return "safe_food_>7"


def bucket_scarcity(value: float | int | None) -> str:
    if value is None:
        return "missing"
    if value <= 1.1:
        return "low_scarcity_<=1.1"
    if value <= 1.7:
        return "medium_scarcity_1.1_1.7"
    if value <= 2.4:
        return "high_scarcity_1.7_2.4"
    return "extreme_scarcity_>2.4"


def bucket_price(value: float | int | None) -> str:
    if value is None:
        return "missing"
    if value <= 2.5:
        return "low_price_<=2.5"
    if value <= 5.0:
        return "medium_price_2.5_5"
    if value <= 7.5:
        return "high_price_5_7.5"
    return "extreme_price_>7.5"


def state_signature(row: dict[str, Any]) -> str:
    """
    Build a stable state signature for duplicate/conflict checks.

    example_id is excluded because two generated examples can have different ids
    while representing the same economic state. Numeric values are rounded to
    reduce tiny formatting differences.
    """
    state = dict(get_state(row))
    state.pop("example_id", None)

    rounded_state: dict[str, Any] = {}
    for key, value in state.items():
        if isinstance(value, float):
            rounded_state[key] = round(value, 3)
        else:
            rounded_state[key] = value

    encoded = json.dumps(rounded_state, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Counters and metrics
# ---------------------------------------------------------------------------


def count_actions(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        action = str(row.get("action", "")).strip().lower()
        if action in ACTIONS:
            counter[action] += 1
        else:
            counter["invalid_or_missing"] += 1
    return counter


def count_buckets(rows: list[dict[str, Any]], field: str, bucket_fn) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        state = get_state(row)
        counter[bucket_fn(as_float(state.get(field)))] += 1
    return counter


def count_rejection_reasons(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        reason = str(row.get("rejection_reason", "missing_rejection_reason"))
        counter[reason] += 1
    return counter


def duplicate_and_conflict_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_signature[state_signature(row)].append(row)

    duplicate_groups = {key: group for key, group in by_signature.items() if len(group) > 1}
    conflict_groups = {}

    for key, group in duplicate_groups.items():
        actions = {str(row.get("action", "")).strip().lower() for row in group}
        actions.discard("")
        if len(actions) > 1:
            conflict_groups[key] = group

    return {
        "unique_signatures": len(by_signature),
        "duplicate_groups": len(duplicate_groups),
        "duplicate_rows": sum(len(group) for group in duplicate_groups.values()),
        "conflict_groups": len(conflict_groups),
        "conflict_rows": sum(len(group) for group in conflict_groups.values()),
    }


def collect_regime_metrics(
    regime: str,
    accepted_rows: list[dict[str, Any]],
    rejected_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    actions = count_actions(accepted_rows)
    total = len(accepted_rows)

    gather = actions.get("gather", 0)
    work = actions.get("work", 0)

    critical_food_total = 0
    critical_food_gather = 0
    high_scarcity_total = 0
    high_scarcity_gather = 0
    safe_food_count = 0

    for row in accepted_rows:
        state = get_state(row)
        food = as_float(state.get("food"))
        scarcity = as_float(state.get("scarcity_ratio"))
        action = str(row.get("action", "")).strip().lower()

        if food is not None and food <= 2.0:
            critical_food_total += 1
            if action == "gather":
                critical_food_gather += 1

        if food is not None and food > 7.0:
            safe_food_count += 1

        if scarcity is not None and scarcity >= 1.7:
            high_scarcity_total += 1
            if action == "gather":
                high_scarcity_gather += 1

    return {
        "regime": regime,
        "accepted_total": total,
        "rejected_total": len(rejected_rows),
        "gather": gather,
        "work": work,
        "gather_ratio": ratio(gather, total),
        "work_ratio": ratio(work, total),
        "critical_food_total": critical_food_total,
        "critical_food_gather": critical_food_gather,
        "critical_food_gather_ratio": ratio(critical_food_gather, critical_food_total),
        "high_scarcity_total": high_scarcity_total,
        "high_scarcity_gather": high_scarcity_gather,
        "high_scarcity_gather_ratio": ratio(high_scarcity_gather, high_scarcity_total),
        "safe_food_count": safe_food_count,
    }


# ---------------------------------------------------------------------------
# Tables and validation logic
# ---------------------------------------------------------------------------


def table_from_counter(counter: Counter[str], total: int) -> str:
    if not counter:
        return "| Item | Count | Ratio |\n|---|---:|---:|\n| none | 0 | 0.0% |\n"

    lines = ["| Item | Count | Ratio |", "|---|---:|---:|"]
    for key, count in sorted(counter.items()):
        lines.append(f"| `{key}` | {count} | {percentage(count, total)} |")
    return "\n".join(lines) + "\n"


def table_from_stats(stats: dict[str, Any]) -> str:
    lines = ["| Metric | Value |", "|---|---:|"]
    for key, value in stats.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines) + "\n"


def regime_warnings_and_failures(
    regime: str,
    accepted_rows: list[dict[str, Any]],
    rejected_rows: list[dict[str, Any]],
    min_examples: int,
) -> tuple[list[str], list[str], dict[str, Any]]:
    warnings: list[str] = []
    failures: list[str] = []
    metrics = collect_regime_metrics(regime, accepted_rows, rejected_rows)
    duplicate_stats = duplicate_and_conflict_stats(accepted_rows)

    total = metrics["accepted_total"]
    rejected_total = metrics["rejected_total"]

    if total == 0:
        return ["No accepted examples found."], ["No accepted examples found."], metrics

    if total < min_examples:
        warnings.append(f"Accepted examples below target minimum: {total} < {min_examples}.")
        failures.append(f"Accepted examples below target minimum: {total} < {min_examples}.")

    if rejected_total > total:
        warnings.append("Rejected examples exceed accepted examples; validators may be too strict or teacher labels may drift.")

    if metrics["critical_food_total"] == 0:
        warnings.append("No critical-food examples found; add states with food <= 2.0.")
        failures.append("No critical-food examples found.")

    if metrics["safe_food_count"] == 0:
        warnings.append("No safe-food examples found; add states with food > 7.0.")
        failures.append("No safe-food examples found.")

    if metrics["high_scarcity_total"] == 0:
        warnings.append("No high-scarcity examples found; add states with scarcity_ratio >= 1.7.")
        failures.append("No high-scarcity examples found.")

    if duplicate_stats["duplicate_groups"] > 0:
        warnings.append("Duplicate state signatures found; dataset may contain repeated states.")
        failures.append("Duplicate state signatures found.")
    if duplicate_stats["conflict_groups"] > 0:
        warnings.append("Conflicting duplicate state signatures found; same state has multiple labels.")
        failures.append("Conflicting duplicate state signatures found.")

    thresholds = STRICT_THRESHOLDS[regime]

    if metrics["critical_food_gather_ratio"] < thresholds["critical_food_gather_ratio"]:
        failures.append(
            "Critical-food gather ratio below strict threshold: "
            f"{metrics['critical_food_gather_ratio']:.2f} < {thresholds['critical_food_gather_ratio']:.2f}."
        )

    if regime == "survival":
        min_gather = thresholds["min_gather_ratio"]
        max_gather = thresholds["max_gather_ratio"]
        if not (min_gather <= metrics["gather_ratio"] <= max_gather):
            failures.append(
                "Survival gather ratio outside strict range: "
                f"{metrics['gather_ratio']:.2f} not in [{min_gather:.2f}, {max_gather:.2f}]."
            )

    if regime == "social_welfare":
        min_gather = thresholds["min_gather_ratio"]
        if metrics["gather_ratio"] < min_gather:
            failures.append(
                "Social-welfare gather ratio below strict threshold: "
                f"{metrics['gather_ratio']:.2f} < {min_gather:.2f}."
            )

        high_scarcity_threshold = thresholds["high_scarcity_gather_ratio"]
        if metrics["high_scarcity_gather_ratio"] < high_scarcity_threshold:
            failures.append(
                "Social-welfare high-scarcity gather ratio below strict threshold: "
                f"{metrics['high_scarcity_gather_ratio']:.2f} < {high_scarcity_threshold:.2f}."
            )

    if regime == "wealth_maximizing":
        min_work = thresholds["min_work_ratio"]
        min_gather = thresholds["min_gather_ratio"]
        if metrics["work_ratio"] < min_work:
            failures.append(
                "Wealth-maximizing work ratio below strict threshold: "
                f"{metrics['work_ratio']:.2f} < {min_work:.2f}."
            )
        if metrics["gather_ratio"] < min_gather:
            failures.append(
                "Wealth-maximizing gather ratio below survival-guardrail minimum: "
                f"{metrics['gather_ratio']:.2f} < {min_gather:.2f}."
            )

    return warnings, failures, metrics


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def load_regime_rows(regime: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    regime_dir = DATA_ROOT / regime
    accepted_path = regime_dir / "teacher_guided_accepted.jsonl"
    rejected_path = regime_dir / "teacher_guided_rejected.jsonl"
    return read_jsonl(accepted_path), read_jsonl(rejected_path)


def build_report(min_examples: int) -> tuple[str, bool]:
    lines = [
        "# Fine-Tune Dataset Validation Report",
        "",
        "This report summarizes the current teacher-guided fine-tune dataset.",
        "",
        "The dataset is generated from synthetic economy states labeled by a Qwen teacher model and filtered by regime-specific validators.",
        "",
    ]

    global_accepted = 0
    global_rejected = 0
    global_actions: Counter[str] = Counter()
    all_failures: dict[str, list[str]] = defaultdict(list)

    for regime in REGIMES:
        accepted_rows, rejected_rows = load_regime_rows(regime)
        accepted_count = len(accepted_rows)
        rejected_count = len(rejected_rows)
        total_seen = accepted_count + rejected_count

        global_accepted += accepted_count
        global_rejected += rejected_count

        actions = count_actions(accepted_rows)
        global_actions.update(actions)

        food_buckets = count_buckets(accepted_rows, "food", bucket_food)
        scarcity_buckets = count_buckets(accepted_rows, "scarcity_ratio", bucket_scarcity)
        price_buckets = count_buckets(accepted_rows, "food_price", bucket_price)
        rejection_reasons = count_rejection_reasons(rejected_rows)
        duplicate_stats = duplicate_and_conflict_stats(accepted_rows)
        warnings, failures, metrics = regime_warnings_and_failures(
            regime=regime,
            accepted_rows=accepted_rows,
            rejected_rows=rejected_rows,
            min_examples=min_examples,
        )
        all_failures[regime] = failures

        lines.extend(
            [
                f"## Regime: `{regime}`",
                "",
                f"Accepted examples: **{accepted_count}**",
                f"Rejected examples: **{rejected_count}**",
                f"Total generated/seen examples: **{total_seen}**",
                f"Acceptance rate: **{percentage(accepted_count, total_seen)}**",
                "",
                "### Strict Metrics",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| `gather_ratio` | {metrics['gather_ratio']:.3f} |",
                f"| `work_ratio` | {metrics['work_ratio']:.3f} |",
                f"| `critical_food_gather_ratio` | {metrics['critical_food_gather_ratio']:.3f} |",
                f"| `high_scarcity_gather_ratio` | {metrics['high_scarcity_gather_ratio']:.3f} |",
                f"| `critical_food_total` | {metrics['critical_food_total']} |",
                f"| `high_scarcity_total` | {metrics['high_scarcity_total']} |",
                "",
                "### Action Distribution",
                "",
                table_from_counter(actions, accepted_count),
                "### Food Coverage",
                "",
                table_from_counter(food_buckets, accepted_count),
                "### Scarcity Coverage",
                "",
                table_from_counter(scarcity_buckets, accepted_count),
                "### Food Price Coverage",
                "",
                table_from_counter(price_buckets, accepted_count),
                "### Duplicate / Conflict Check",
                "",
                table_from_stats(duplicate_stats),
                "### Rejection Reasons",
                "",
                table_from_counter(rejection_reasons, rejected_count),
                "### Warnings",
                "",
            ]
        )

        if warnings:
            for warning in warnings:
                lines.append(f"- {warning}")
        else:
            lines.append("- No warnings.")

        lines.extend(["", "### Strict Failures", ""])
        if failures:
            for failure in failures:
                lines.append(f"- {failure}")
        else:
            lines.append("- No strict failures.")

        lines.append("")

    total_global = global_accepted + global_rejected
    has_failures = any(all_failures.values())

    lines.extend(
        [
            "## Global Summary",
            "",
            f"Total accepted examples: **{global_accepted}**",
            f"Total rejected examples: **{global_rejected}**",
            f"Total seen examples: **{total_global}**",
            f"Global acceptance rate: **{percentage(global_accepted, total_global)}**",
            f"Strict validation status: **{'FAIL' if has_failures else 'PASS'}**",
            "",
            "### Global Action Distribution",
            "",
            table_from_counter(global_actions, global_accepted),
            "### Next Steps",
            "",
            "- If strict validation passes, generate a larger teacher-guided dataset.",
            "- If a regime has poor coverage, generate more targeted states for that regime.",
            "- Keep teacher labels validator-filtered before training LoRA adapters.",
            "",
        ]
    )

    return "\n".join(lines), has_failures


def print_console_summary(report: str) -> None:
    interesting_prefixes = (
        "## Regime:",
        "Accepted examples:",
        "Rejected examples:",
        "Acceptance rate:",
        "Strict validation status:",
        "## Global Summary",
        "Total accepted examples:",
        "Total rejected examples:",
        "Global acceptance rate:",
    )

    for line in report.splitlines():
        if line.startswith(interesting_prefixes):
            print(line.replace("**", ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate fine-tune JSONL datasets.")
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--min-examples",
        type=int,
        default=100,
        help="Minimum accepted examples expected per regime.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if strict validation fails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report, has_failures = build_report(min_examples=args.min_examples)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print_console_summary(report)
    print(f"\nWrote dataset validation report to: {report_path}")

    if args.strict and has_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Validate teacher-guided fine-tune datasets for the AI Society project.

This script reads accepted/rejected JSONL files under data/finetune/<regime>/
and reports:
- accepted/rejected counts
- gather/work action distribution
- rejection reasons
- food/scarcity/price bucket coverage
- basic regime-specific sanity checks

It writes a Markdown report to analysis/finetune_dataset_report.md by default.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "finetune"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "analysis" / "finetune_dataset_report.md"

REGIMES = ["survival", "social_welfare", "wealth_maximizing"]
ACTIONS = {"gather", "work"}


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


def table_from_counter(counter: Counter[str], total: int) -> str:
    if not counter:
        return "| Item | Count | Ratio |\n|---|---:|---:|\n| none | 0 | 0.0% |\n"

    lines = ["| Item | Count | Ratio |", "|---|---:|---:|"]
    for key, count in sorted(counter.items()):
        lines.append(f"| `{key}` | {count} | {percentage(count, total)} |")
    return "\n".join(lines) + "\n"


def regime_warnings(regime: str, accepted_rows: list[dict[str, Any]], rejected_rows: list[dict[str, Any]]) -> list[str]:
    warnings = []
    total = len(accepted_rows)
    rejected_total = len(rejected_rows)
    actions = count_actions(accepted_rows)

    gather = actions.get("gather", 0)
    work = actions.get("work", 0)

    if total == 0:
        return ["No accepted examples found."]

    if rejected_total > total:
        warnings.append("Rejected examples exceed accepted examples; validators may be too strict or teacher labels may drift.")

    critical_food_count = 0
    high_scarcity_count = 0
    safe_food_count = 0

    high_scarcity_gather = 0
    high_scarcity_total = 0

    critical_food_gather = 0
    critical_food_total = 0

    for row in accepted_rows:
        state = get_state(row)
        food = as_float(state.get("food"))
        scarcity = as_float(state.get("scarcity_ratio"))
        action = str(row.get("action", "")).strip().lower()

        if food is not None and food <= 2.0:
            critical_food_count += 1
            critical_food_total += 1
            if action == "gather":
                critical_food_gather += 1

        if food is not None and food > 7.0:
            safe_food_count += 1

        if scarcity is not None and scarcity >= 1.7:
            high_scarcity_count += 1
            high_scarcity_total += 1
            if action == "gather":
                high_scarcity_gather += 1

    if critical_food_count == 0:
        warnings.append("No critical-food examples found; add states with food <= 2.0.")

    if safe_food_count == 0:
        warnings.append("No safe-food examples found; add states with food > 7.0.")

    if high_scarcity_count == 0:
        warnings.append("No high-scarcity examples found; add states with scarcity_ratio >= 1.7.")

    if critical_food_total > 0 and critical_food_gather < critical_food_total:
        warnings.append("Some critical-food accepted examples are not gather; check survival guardrails.")

    if regime == "wealth_maximizing":
        if work <= gather:
            warnings.append("Wealth-maximizing accepted set is not work-heavy; expected more work than gather.")
        if gather == 0:
            warnings.append("Wealth-maximizing has no gather examples; add survival guardrail cases.")

    if regime == "social_welfare":
        if high_scarcity_total > 0 and high_scarcity_gather < max(1, high_scarcity_total // 2):
            warnings.append("Social-welfare high-scarcity examples are not gather-heavy enough.")

    if regime == "survival":
        gather_ratio = gather / total
        if gather_ratio < 0.25 or gather_ratio > 0.75:
            warnings.append("Survival is not balanced; gather ratio should usually stay between 25% and 75%.")

    return warnings


def load_regime_rows(regime: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    regime_dir = DATA_ROOT / regime
    accepted_path = regime_dir / "teacher_guided_accepted.jsonl"
    rejected_path = regime_dir / "teacher_guided_rejected.jsonl"
    return read_jsonl(accepted_path), read_jsonl(rejected_path)


def build_report() -> str:
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
    global_warnings: dict[str, list[str]] = defaultdict(list)

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
        warnings = regime_warnings(regime, accepted_rows, rejected_rows)
        global_warnings[regime] = warnings

        lines.extend(
            [
                f"## Regime: `{regime}`",
                "",
                f"Accepted examples: **{accepted_count}**",
                f"Rejected examples: **{rejected_count}**",
                f"Total generated/seen examples: **{total_seen}**",
                f"Acceptance rate: **{percentage(accepted_count, total_seen)}**",
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

        lines.append("")

    total_global = global_accepted + global_rejected
    lines.extend(
        [
            "## Global Summary",
            "",
            f"Total accepted examples: **{global_accepted}**",
            f"Total rejected examples: **{global_rejected}**",
            f"Total seen examples: **{total_global}**",
            f"Global acceptance rate: **{percentage(global_accepted, total_global)}**",
            "",
            "### Global Action Distribution",
            "",
            table_from_counter(global_actions, global_accepted),
            "### Next Steps",
            "",
            "- If warnings are acceptable, generate a larger teacher-guided dataset.",
            "- If a regime has poor coverage, generate more targeted states for that regime.",
            "- Keep teacher labels validator-filtered before training LoRA adapters.",
            "",
        ]
    )

    return "\n".join(lines)


def print_console_summary(report: str) -> None:
    interesting_prefixes = (
        "## Regime:",
        "Accepted examples:",
        "Rejected examples:",
        "Acceptance rate:",
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report()

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print_console_summary(report)
    print(f"\nWrote dataset validation report to: {report_path}")


if __name__ == "__main__":
    main()
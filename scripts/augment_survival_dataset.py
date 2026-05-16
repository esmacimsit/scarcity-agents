#!/usr/bin/env python3
"""
Failure-driven survival dataset augmentation for the AI Society project.

Purpose:
- Keep the validated teacher-guided survival dataset as the gold source.
- Add controlled synthetic examples around survival gather-risk regions.
- Improve gather recall for medium-food crisis states without destroying safe-work behavior.

Input:
  data/finetune/survival/teacher_guided_accepted.jsonl

Output:
  data/finetune/survival/survival_augmented_accepted.jsonl
  data/finetune/survival/survival_combined_accepted.jsonl
  analysis/survival_augmentation_report.md

This script does not call any external API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "finetune" / "survival" / "teacher_guided_accepted.jsonl"
AUGMENTED_PATH = PROJECT_ROOT / "data" / "finetune" / "survival" / "survival_augmented_accepted.jsonl"
COMBINED_PATH = PROJECT_ROOT / "data" / "finetune" / "survival" / "survival_combined_accepted.jsonl"
REPORT_PATH = PROJECT_ROOT / "analysis" / "survival_augmentation_report.md"

ACTIONS = {"gather", "work"}


@dataclass(frozen=True)
class AugmentationStats:
    original_total: int
    original_gather: int
    original_work: int
    augmented_total: int
    augmented_gather: int
    augmented_work: int
    combined_total: int
    combined_gather: int
    combined_work: int
    rejected_candidates: int
    duplicate_candidates: int


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def round_float(value: float) -> float:
    return round(value, 4)


def clamp_float(value: float, low: float, high: float) -> float:
    return round_float(max(low, min(high, value)))


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def get_state(row: dict[str, Any]) -> dict[str, Any]:
    state = row.get("state")
    if not isinstance(state, dict):
        raise ValueError("Missing state dict in row.")
    return state


def get_action(row: dict[str, Any]) -> str:
    action = str(row.get("action", "")).strip().lower()
    if action not in ACTIONS:
        raise ValueError(f"Invalid action: {action!r}")
    return action


def state_signature_from_state(state: dict[str, Any]) -> str:
    data = dict(state)
    data.pop("example_id", None)

    rounded: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, float):
            rounded[key] = round(value, 3)
        else:
            rounded[key] = value

    encoded = json.dumps(rounded, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def state_signature(row: dict[str, Any]) -> str:
    return state_signature_from_state(get_state(row))


def is_survival_gather_risk_seed(row: dict[str, Any]) -> bool:
    if get_action(row) != "gather":
        return False

    state = get_state(row)
    return (
        2.0 < float(state["food"]) <= 6.2
        and float(state["food_price"]) >= 4.5
        and float(state["scarcity_ratio"]) >= 1.5
        and int(state["dead_total"]) >= 8
    )


def is_survival_safe_work_seed(row: dict[str, Any]) -> bool:
    if get_action(row) != "work":
        return False

    state = get_state(row)
    return (
        float(state["food"]) >= 7.0
        and float(state["food_price"]) <= 3.0
        and float(state["scarcity_ratio"]) <= 1.2
        and int(state["dead_total"]) <= 5
    )


def survival_guardrail_reason(state: dict[str, Any], action: str) -> str | None:
    """Return None if an augmented row is still label-preserving enough."""
    food = float(state["food"])
    coin = float(state["coin"])
    food_price = float(state["food_price"])
    scarcity_ratio = float(state["scarcity_ratio"])
    dead_total = int(state["dead_total"])

    if action == "gather":
        # Critical food always supports gather.
        if food <= 2.0:
            return None

        # Main failure-driven bucket: medium-food crisis state.
        if food <= 6.2 and food_price >= 4.5 and scarcity_ratio >= 1.5 and dead_total >= 8:
            return None

        # High-price/high-scarcity state may still justify gather even with lower deaths.
        if food <= 5.5 and food_price >= 5.5 and scarcity_ratio >= 1.8:
            return None

        return "gather_augmented_state_left_survival_risk_region"

    if action == "work":
        if food >= 7.0 and food_price <= 3.0 and scarcity_ratio <= 1.2 and dead_total <= 5:
            return None
        if food >= 8.0 and coin <= 2.0 and food_price <= 2.5 and scarcity_ratio <= 1.2:
            return None
        return "work_augmented_state_left_safe_work_region"

    return "invalid_action"


def perturb_gather_state(base_state: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    state = dict(base_state)

    state["food"] = clamp_float(float(state["food"]) + rng.uniform(-0.45, 0.35), 2.05, 6.2)
    state["coin"] = clamp_float(float(state["coin"]) + rng.uniform(-1.0, 1.0), 0.0, 12.0)
    state["productivity"] = clamp_float(float(state["productivity"]) + rng.uniform(-0.08, 0.08), 0.7, 1.4)
    state["food_price"] = clamp_float(float(state["food_price"]) + rng.uniform(-0.55, 0.65), 4.5, 10.0)
    state["scarcity_ratio"] = clamp_float(float(state["scarcity_ratio"]) + rng.uniform(-0.25, 0.3), 1.5, 3.5)
    state["dead_total"] = clamp_int(int(state["dead_total"]) + rng.randint(-3, 4), 8, 40)
    state["alive_count"] = clamp_int(int(state["alive_count"]) + rng.randint(-3, 3), 10, 50)
    state["timestep"] = clamp_int(int(state["timestep"]) + rng.randint(-4, 4), 0, 80)

    state["wealth"] = round_float(float(state["coin"]) + (float(state["food"]) * float(state["food_price"])))
    state["total_food"] = clamp_float(float(state["total_food"]) + rng.uniform(-20.0, 20.0), 10.0, 400.0)
    return state


def perturb_work_state(base_state: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    state = dict(base_state)

    state["food"] = clamp_float(float(state["food"]) + rng.uniform(-0.4, 0.5), 7.0, 12.5)
    state["coin"] = clamp_float(float(state["coin"]) + rng.uniform(-0.8, 0.8), 0.0, 8.0)
    state["productivity"] = clamp_float(float(state["productivity"]) + rng.uniform(-0.08, 0.08), 0.7, 1.4)
    state["food_price"] = clamp_float(float(state["food_price"]) + rng.uniform(-0.25, 0.25), 0.8, 3.0)
    state["scarcity_ratio"] = clamp_float(float(state["scarcity_ratio"]) + rng.uniform(-0.15, 0.15), 0.45, 1.2)
    state["dead_total"] = clamp_int(int(state["dead_total"]) + rng.randint(-1, 1), 0, 5)
    state["alive_count"] = clamp_int(int(state["alive_count"]) + rng.randint(-2, 2), 35, 50)
    state["timestep"] = clamp_int(int(state["timestep"]) + rng.randint(-4, 4), 0, 80)

    state["wealth"] = round_float(float(state["coin"]) + (float(state["food"]) * float(state["food_price"])))
    state["total_food"] = clamp_float(float(state["total_food"]) + rng.uniform(-20.0, 20.0), 35.0, 400.0)
    return state


def make_augmented_row(
    source_row: dict[str, Any],
    new_state: dict[str, Any],
    action: str,
    synthetic_id: str,
    bucket: str,
) -> dict[str, Any]:
    new_state = dict(new_state)
    new_state["example_id"] = synthetic_id
    new_state["regime"] = "survival"

    return {
        "source": "synthetic_failure_driven_survival_augmented",
        "base_source": source_row.get("source", "teacher_guided"),
        "teacher_model": source_row.get("teacher_model"),
        "regime": "survival",
        "state": new_state,
        "action": action,
        "augmentation_bucket": bucket,
        "base_example_id": get_state(source_row).get("example_id"),
    }


def build_augmented_rows(
    rows: list[dict[str, Any]],
    gather_target: int,
    work_target: int,
    seed: int,
) -> tuple[list[dict[str, Any]], int, int]:
    rng = random.Random(seed)

    gather_seeds = [row for row in rows if is_survival_gather_risk_seed(row)]
    work_seeds = [row for row in rows if is_survival_safe_work_seed(row)]

    if not gather_seeds:
        raise RuntimeError("No gather-risk seeds found for survival augmentation.")
    if not work_seeds:
        raise RuntimeError("No safe-work seeds found for survival augmentation.")

    existing_signatures = {state_signature(row) for row in rows}
    augmented_rows: list[dict[str, Any]] = []
    rejected_candidates = 0
    duplicate_candidates = 0

    def add_examples(target: int, action: str, seeds: list[dict[str, Any]], bucket: str) -> None:
        nonlocal rejected_candidates, duplicate_candidates
        attempts = 0
        max_attempts = target * 50

        while sum(1 for row in augmented_rows if row["action"] == action) < target and attempts < max_attempts:
            attempts += 1
            base_row = rng.choice(seeds)
            base_state = get_state(base_row)

            if action == "gather":
                new_state = perturb_gather_state(base_state, rng)
            else:
                new_state = perturb_work_state(base_state, rng)

            reason = survival_guardrail_reason(new_state, action)
            if reason is not None:
                rejected_candidates += 1
                continue

            signature = state_signature_from_state(new_state)
            if signature in existing_signatures:
                duplicate_candidates += 1
                continue

            synthetic_index = len(augmented_rows) + 1
            synthetic_id = f"survival_aug_{synthetic_index:05d}"
            row = make_augmented_row(
                source_row=base_row,
                new_state=new_state,
                action=action,
                synthetic_id=synthetic_id,
                bucket=bucket,
            )
            augmented_rows.append(row)
            existing_signatures.add(signature)

        actual = sum(1 for row in augmented_rows if row["action"] == action)
        if actual < target:
            raise RuntimeError(f"Could only generate {actual}/{target} synthetic {action} examples.")

    add_examples(
        target=gather_target,
        action="gather",
        seeds=gather_seeds,
        bucket="medium_food_high_price_scarcity_deaths_gather",
    )
    add_examples(
        target=work_target,
        action="work",
        seeds=work_seeds,
        bucket="safe_food_low_scarcity_work",
    )

    return augmented_rows, rejected_candidates, duplicate_candidates


def action_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[get_action(row)] += 1
    return counter


def assert_no_duplicate_conflicts(rows: list[dict[str, Any]]) -> None:
    seen: dict[str, str] = {}
    duplicates = 0
    conflicts = 0

    for row in rows:
        signature = state_signature(row)
        action = get_action(row)
        if signature in seen:
            duplicates += 1
            if seen[signature] != action:
                conflicts += 1
        else:
            seen[signature] = action

    if duplicates:
        raise RuntimeError(f"Duplicate state signatures found after augmentation: {duplicates}")
    if conflicts:
        raise RuntimeError(f"Conflicting duplicate labels found after augmentation: {conflicts}")


def write_report(stats: AugmentationStats, gather_target: int, work_target: int) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# Survival Dataset Augmentation Report

## Purpose

Failure-driven augmentation was applied to the survival dataset after the first Qwen3-8B survival adapter showed a work bias on validation probes.

Observed v1 issue:

```text
work recall:   strong
gather recall: weaker
main error:    gather → work
```

The augmentation focuses on medium-food survival crisis states where the correct action should remain `gather`.

## Input Dataset

```text
input: {INPUT_PATH.relative_to(PROJECT_ROOT)}
original total: {stats.original_total}
original gather: {stats.original_gather}
original work: {stats.original_work}
```

## Synthetic Targets

```text
target synthetic gather-risk examples: {gather_target}
target synthetic safe-work examples:   {work_target}
```

## Generated Dataset

```text
augmented total: {stats.augmented_total}
augmented gather: {stats.augmented_gather}
augmented work: {stats.augmented_work}

combined total: {stats.combined_total}
combined gather: {stats.combined_gather}
combined work: {stats.combined_work}
```

## Candidate Filtering

```text
rejected candidates: {stats.rejected_candidates}
duplicate candidates: {stats.duplicate_candidates}
```

## Output Files

```text
augmented: {AUGMENTED_PATH.relative_to(PROJECT_ROOT)}
combined:  {COMBINED_PATH.relative_to(PROJECT_ROOT)}
```

## Notes

The original teacher-guided dataset remains unchanged.

The combined dataset should be converted into a separate LoRA v2 dataset and trained into a separate adapter path, for example:

```text
data/lora_v2/survival
adapters/qwen3_8b_survival_v2
```
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create failure-driven survival augmentation data.")
    parser.add_argument("--input", default=str(INPUT_PATH), help="Input teacher-guided accepted JSONL.")
    parser.add_argument("--augmented-output", default=str(AUGMENTED_PATH), help="Augmented output JSONL.")
    parser.add_argument("--combined-output", default=str(COMBINED_PATH), help="Combined output JSONL.")
    parser.add_argument("--gather-target", type=int, default=250, help="Synthetic gather examples to generate.")
    parser.add_argument("--work-target", type=int, default=100, help="Synthetic work examples to generate.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    global INPUT_PATH, AUGMENTED_PATH, COMBINED_PATH
    INPUT_PATH = Path(args.input)
    AUGMENTED_PATH = Path(args.augmented_output)
    COMBINED_PATH = Path(args.combined_output)

    original_rows = read_jsonl(INPUT_PATH)
    original_counts = action_counts(original_rows)

    augmented_rows, rejected_candidates, duplicate_candidates = build_augmented_rows(
        rows=original_rows,
        gather_target=args.gather_target,
        work_target=args.work_target,
        seed=args.seed,
    )
    augmented_counts = action_counts(augmented_rows)

    combined_rows = original_rows + augmented_rows
    assert_no_duplicate_conflicts(combined_rows)
    combined_counts = action_counts(combined_rows)

    write_jsonl(AUGMENTED_PATH, augmented_rows)
    write_jsonl(COMBINED_PATH, combined_rows)

    stats = AugmentationStats(
        original_total=len(original_rows),
        original_gather=original_counts.get("gather", 0),
        original_work=original_counts.get("work", 0),
        augmented_total=len(augmented_rows),
        augmented_gather=augmented_counts.get("gather", 0),
        augmented_work=augmented_counts.get("work", 0),
        combined_total=len(combined_rows),
        combined_gather=combined_counts.get("gather", 0),
        combined_work=combined_counts.get("work", 0),
        rejected_candidates=rejected_candidates,
        duplicate_candidates=duplicate_candidates,
    )
    write_report(stats, gather_target=args.gather_target, work_target=args.work_target)

    print("=" * 80)
    print("Survival augmentation complete")
    print(f"Original:  total={stats.original_total} gather={stats.original_gather} work={stats.original_work}")
    print(f"Augmented: total={stats.augmented_total} gather={stats.augmented_gather} work={stats.augmented_work}")
    print(f"Combined:  total={stats.combined_total} gather={stats.combined_gather} work={stats.combined_work}")
    print(f"Rejected candidates: {stats.rejected_candidates}")
    print(f"Duplicate candidates: {stats.duplicate_candidates}")
    print(f"Wrote augmented dataset to: {AUGMENTED_PATH}")
    print(f"Wrote combined dataset to: {COMBINED_PATH}")
    print(f"Wrote report to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
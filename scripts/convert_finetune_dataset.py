#!/usr/bin/env python3
"""
Convert teacher-guided decision datasets into LoRA training/validation JSONL files.

Input:
  data/finetune/<regime>/teacher_guided_accepted.jsonl

Output:
  data/lora/<regime>/train.jsonl
  data/lora/<regime>/valid.jsonl

The output format is chat-style JSONL:

{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "gather"}]}

This script does not call any external API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINETUNE_ROOT = PROJECT_ROOT / "data" / "finetune"
LORA_ROOT = PROJECT_ROOT / "data" / "lora"

REGIMES = ["survival", "social_welfare", "wealth_maximizing"]
ACTIONS = {"gather", "work"}


SYSTEM_PROMPTS = {
    "survival": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the survival regime. Prioritize long-term personal survival. "
        "Choose gather when food is low or scarcity is dangerous. Choose work when food is safe and coin is needed. "
        "Return exactly one action: gather or work."
    ),
    "social_welfare": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the social welfare regime. Prioritize survival while reducing society-level scarcity, deaths, and high food prices. "
        "Choose gather during collective crisis. Choose work only when the agent and society are relatively stable. "
        "Return exactly one action: gather or work."
    ),
    "wealth_maximizing": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the wealth-maximizing regime. Prioritize coin and wealth when personal survival is safe. "
        "Choose gather only when personal survival is at risk. Be selfish but not suicidal. "
        "Return exactly one action: gather or work."
    ),
}


STATE_FIELDS = [
    "timestep",
    "food",
    "coin",
    "productivity",
    "wealth",
    "food_price",
    "alive_count",
    "dead_total",
    "total_food",
    "scarcity_ratio",
]


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_state(row: dict[str, Any]) -> dict[str, Any]:
    state = row.get("state")
    if not isinstance(state, dict):
        return {}
    return state


def normalize_action(row: dict[str, Any]) -> str:
    action = str(row.get("action", "")).strip().lower()
    if action not in ACTIONS:
        raise ValueError(f"Invalid action: {action!r}")
    return action


def state_signature(row: dict[str, Any]) -> str:
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


def assert_no_duplicate_or_conflict(rows: list[dict[str, Any]], regime: str) -> None:
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

    if duplicate_groups:
        raise ValueError(
            f"Duplicate state signatures found for regime={regime}: {len(duplicate_groups)} duplicate groups. "
            "Run validation before converting."
        )

    if conflict_groups:
        raise ValueError(
            f"Conflicting duplicate labels found for regime={regime}: {len(conflict_groups)} conflict groups."
        )


def format_state_for_prompt(state: dict[str, Any]) -> str:
    lines = ["Economy state:"]
    for field in STATE_FIELDS:
        value = state.get(field)
        lines.append(f"- {field}: {value}")
    lines.append("")
    lines.append("Choose exactly one action: gather or work.")
    return "\n".join(lines)


def to_chat_example(row: dict[str, Any], regime: str) -> dict[str, Any]:
    state = get_state(row)
    action = normalize_action(row)

    if not state:
        raise ValueError(f"Missing state for regime={regime}")

    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPTS[regime],
            },
            {
                "role": "user",
                "content": format_state_for_prompt(state),
            },
            {
                "role": "assistant",
                "content": action,
            },
        ],
        "metadata": {
            "source": row.get("source", "teacher_guided"),
            "teacher_model": row.get("teacher_model"),
            "regime": regime,
            "example_id": state.get("example_id"),
            "action": action,
        },
    }


def split_rows(rows: list[dict[str, Any]], valid_ratio: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.0 < valid_ratio < 0.5:
        raise ValueError("valid_ratio must be between 0.0 and 0.5")

    shuffled = list(rows)
    rng = random.Random(seed)
    rng.shuffle(shuffled)

    valid_count = max(1, round(len(shuffled) * valid_ratio))
    valid_rows = shuffled[:valid_count]
    train_rows = shuffled[valid_count:]
    return train_rows, valid_rows


def action_distribution(rows: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[normalize_action(row)] += 1
    return counter


def percentage(part: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def convert_regime(regime: str, valid_ratio: float, seed: int, overwrite: bool) -> dict[str, Any]:
    input_path = FINETUNE_ROOT / regime / "teacher_guided_accepted.jsonl"
    output_dir = LORA_ROOT / regime
    train_path = output_dir / "train.jsonl"
    valid_path = output_dir / "valid.jsonl"

    if not overwrite and (train_path.exists() or valid_path.exists()):
        raise FileExistsError(
            f"Output already exists for regime={regime}. Use --overwrite to regenerate."
        )

    rows = read_jsonl(input_path)
    if not rows:
        raise FileNotFoundError(f"No accepted examples found at {input_path}")

    assert_no_duplicate_or_conflict(rows, regime)

    train_rows, valid_rows = split_rows(
        rows=rows,
        valid_ratio=valid_ratio,
        seed=seed + REGIMES.index(regime),
    )

    train_examples = [to_chat_example(row, regime) for row in train_rows]
    valid_examples = [to_chat_example(row, regime) for row in valid_rows]

    write_jsonl(train_path, train_examples)
    write_jsonl(valid_path, valid_examples)

    return {
        "regime": regime,
        "input": str(input_path.relative_to(PROJECT_ROOT)),
        "train": str(train_path.relative_to(PROJECT_ROOT)),
        "valid": str(valid_path.relative_to(PROJECT_ROOT)),
        "total": len(rows),
        "train_count": len(train_examples),
        "valid_count": len(valid_examples),
        "valid_ratio": valid_ratio,
        "action_distribution": dict(action_distribution(rows)),
        "train_action_distribution": dict(action_distribution(train_rows)),
        "valid_action_distribution": dict(action_distribution(valid_rows)),
    }


def write_summary(summary: list[dict[str, Any]]) -> None:
    summary_path = LORA_ROOT / "conversion_summary.md"
    LORA_ROOT.mkdir(parents=True, exist_ok=True)

    lines = [
        "# LoRA Dataset Conversion Summary",
        "",
        "Teacher-guided accepted examples were converted into chat-style LoRA train/validation JSONL files.",
        "",
        "| Regime | Total | Train | Valid | Gather | Work |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for item in summary:
        actions = item["action_distribution"]
        lines.append(
            f"| `{item['regime']}` | {item['total']} | {item['train_count']} | {item['valid_count']} | "
            f"{actions.get('gather', 0)} | {actions.get('work', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Output Paths",
            "",
        ]
    )

    for item in summary:
        lines.extend(
            [
                f"### `{item['regime']}`",
                "",
                f"- Train: `{item['train']}`",
                f"- Valid: `{item['valid']}`",
                "",
            ]
        )

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert accepted fine-tune datasets to LoRA chat JSONL format.")
    parser.add_argument(
        "--regimes",
        nargs="+",
        default=REGIMES,
        choices=REGIMES,
        help="Regimes to convert.",
    )
    parser.add_argument(
        "--valid-ratio",
        type=float,
        default=0.10,
        help="Validation split ratio.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for train/validation split.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing converted train/valid files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary = []
    for regime in args.regimes:
        result = convert_regime(
            regime=regime,
            valid_ratio=args.valid_ratio,
            seed=args.seed,
            overwrite=args.overwrite,
        )
        summary.append(result)

        actions = result["action_distribution"]
        print("=" * 80)
        print(f"Converted regime: {regime}")
        print(f"Input examples: {result['total']}")
        print(f"Train examples: {result['train_count']}")
        print(f"Valid examples: {result['valid_count']}")
        print(
            "Action distribution: "
            f"gather={actions.get('gather', 0)} ({percentage(actions.get('gather', 0), result['total'])}), "
            f"work={actions.get('work', 0)} ({percentage(actions.get('work', 0), result['total'])})"
        )
        print(f"Train path: {result['train']}")
        print(f"Valid path: {result['valid']}")

    write_summary(summary)
    print("=" * 80)
    print("Done. LoRA datasets written under:", LORA_ROOT)
    print("Summary written to:", LORA_ROOT / "conversion_summary.md")


if __name__ == "__main__":
    main()

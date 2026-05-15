#!/usr/bin/env python3
"""
Generate teacher-guided fine-tuning decision labels for the AI Society project.

This script uses a large Qwen teacher model through Hugging Face Inference
Providers to label synthetic economy states as either `gather` or `work`.

Important:
- HF_TOKEN must be set in the environment.
- The teacher output is not accepted blindly.
- Every label is checked by regime-specific validators.

Default behavior is intentionally small:
- 10 accepted examples per regime
- 5 candidate states per teacher batch

Increase the counts only after checking the pilot output.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from huggingface_hub import InferenceClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "finetune"

MODEL_ID = "Qwen/Qwen3-235B-A22B-Instruct-2507:novita"
REGIMES = ["survival", "social_welfare", "wealth_maximizing"]
ACTIONS = {"gather", "work"}


@dataclass(frozen=True)
class EconomyState:
    example_id: str
    regime: str
    timestep: int
    food: float
    coin: float
    productivity: float
    wealth: float
    food_price: float
    alive_count: int
    dead_total: int
    total_food: float
    scarcity_ratio: float


@dataclass(frozen=True)
class TeacherLabel:
    example_id: str
    regime: str
    action: str


def round_float(value: float) -> float:
    return round(value, 4)


def make_state(regime: str, index: int, rng: random.Random) -> EconomyState:
    """Generate one synthetic economy state."""
    scenario_type = rng.choice(["safe", "medium", "scarce", "critical"])

    if scenario_type == "safe":
        food = rng.uniform(6.5, 12.0)
        coin = rng.uniform(0.0, 6.0)
        food_price = rng.uniform(0.8, 2.4)
        scarcity_ratio = rng.uniform(0.5, 1.1)
        dead_total = rng.randint(0, 3)
        alive_count = rng.randint(42, 50)
    elif scenario_type == "medium":
        food = rng.uniform(3.5, 8.0)
        coin = rng.uniform(0.0, 8.0)
        food_price = rng.uniform(2.0, 4.8)
        scarcity_ratio = rng.uniform(1.0, 1.7)
        dead_total = rng.randint(0, 10)
        alive_count = rng.randint(35, 50)
    elif scenario_type == "scarce":
        food = rng.uniform(1.8, 6.0)
        coin = rng.uniform(0.0, 10.0)
        food_price = rng.uniform(4.2, 8.0)
        scarcity_ratio = rng.uniform(1.6, 2.7)
        dead_total = rng.randint(8, 25)
        alive_count = rng.randint(20, 42)
    else:
        food = rng.uniform(0.0, 2.6)
        coin = rng.uniform(0.0, 12.0)
        food_price = rng.uniform(6.0, 10.0)
        scarcity_ratio = rng.uniform(2.2, 3.5)
        dead_total = rng.randint(18, 40)
        alive_count = rng.randint(10, 32)

    productivity = rng.uniform(0.7, 1.4)
    wealth = coin + (food * food_price)
    total_food = rng.uniform(alive_count * 1.0, alive_count * 8.0)

    return EconomyState(
        example_id=f"{regime}_{index:05d}",
        regime=regime,
        timestep=rng.randint(0, 80),
        food=round_float(food),
        coin=round_float(coin),
        productivity=round_float(productivity),
        wealth=round_float(wealth),
        food_price=round_float(food_price),
        alive_count=alive_count,
        dead_total=dead_total,
        total_food=round_float(total_food),
        scarcity_ratio=round_float(scarcity_ratio),
    )


def regime_description(regime: str) -> str:
    if regime == "survival":
        return (
            "This regime is balanced and survival-oriented. "
            "Protect the agent's long-term survival. Choose gather when food is low, "
            "food price is high, or scarcity is rising. Choose work when food is safe "
            "and the agent needs coin."
        )

    if regime == "social_welfare":
        return (
            "This regime is society-aware. The agent should survive while reducing "
            "society-level scarcity, deaths, and inequality. Choose gather when food "
            "price, scarcity, or deaths are high. Work is acceptable only when the "
            "agent and society are relatively stable."
        )

    if regime == "wealth_maximizing":
        return (
            "This regime is self-interested and wealth-maximizing. Prioritize coin "
            "and wealth when personal survival is safe. Choose gather only when the "
            "agent's own survival is at risk. Do not optimize society-level welfare "
            "unless it affects personal survival. The target is selfish but not suicidal."
        )

    raise ValueError(f"Unknown regime: {regime}")


def state_for_prompt(state: EconomyState) -> dict[str, Any]:
    data = asdict(state)
    data.pop("regime")
    return data


def build_teacher_prompt(regime: str, states: list[EconomyState]) -> str:
    items = [state_for_prompt(state) for state in states]

    return f"""You are labeling training data for a scarcity-based economy simulation.

Behavior regime: {regime}

{regime_description(regime)}

Each item is one agent state. Choose exactly one action for each item:
- gather
- work

Return valid JSON only.
Do not include markdown.
Do not explain your choices.

Return format:
[
  {{"example_id": "...", "action": "gather"}},
  {{"example_id": "...", "action": "work"}}
]

Items:
{json.dumps(items, indent=2)}
"""


def extract_json_array(text: str) -> list[dict[str, Any]]:
    """Parse a JSON array from the teacher response."""
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Could not find JSON array in response: {text[:300]}")

    parsed = json.loads(match.group(0))
    if not isinstance(parsed, list):
        raise ValueError("Teacher response JSON is not a list.")

    return parsed


def normalize_teacher_labels(response_text: str, regime: str) -> list[TeacherLabel]:
    parsed = extract_json_array(response_text)
    labels = []

    for item in parsed:
        example_id = str(item.get("example_id", "")).strip()
        action = str(item.get("action", "")).strip().lower()

        if action not in ACTIONS:
            continue

        labels.append(
            TeacherLabel(
                example_id=example_id,
                regime=regime,
                action=action,
            )
        )

    return labels


def validation_reason(state: EconomyState, action: str) -> str | None:
    """
    Return None if the teacher label is acceptable.
    Return a rejection reason if it violates a hard regime-specific guardrail.
    """
    if action not in ACTIONS:
        return "invalid_action"

    if state.regime == "survival":
        if state.food <= 2.0 and action != "gather":
            return "survival_food_critical_requires_gather"
        if (
            state.food >= 8.0
            and state.coin <= 1.5
            and state.food_price <= 2.5
            and state.scarcity_ratio <= 1.2
            and action != "work"
        ):
            return "survival_safe_low_coin_allows_work"
        return None

    if state.regime == "social_welfare":
        if state.food_price >= 5.5 and state.scarcity_ratio >= 1.8 and action != "gather":
            return "social_welfare_high_price_scarcity_requires_gather"
        if state.dead_total >= 15 and state.scarcity_ratio >= 1.6 and action != "gather":
            return "social_welfare_deaths_scarcity_requires_gather"
        return None

    if state.regime == "wealth_maximizing":
        if state.food <= 2.0 and action != "gather":
            return "wealth_food_critical_requires_gather"
        if (
            state.food >= 7.0
            and state.coin <= 2.0
            and state.scarcity_ratio <= 1.6
            and action != "work"
        ):
            return "wealth_safe_low_coin_prefers_work"
        if state.food >= 8.0 and state.food_price <= 3.0 and action != "work":
            return "wealth_safe_cheap_food_prefers_work"
        return None

    return f"unknown_regime_{state.regime}"


def write_jsonl(path: Path, rows: list[dict[str, Any]], append: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def output_paths(regime: str) -> dict[str, Path]:
    regime_dir = DATA_ROOT / regime
    return {
        "raw": regime_dir / "teacher_guided_raw.jsonl",
        "accepted": regime_dir / "teacher_guided_accepted.jsonl",
        "rejected": regime_dir / "teacher_guided_rejected.jsonl",
    }


def call_teacher(
    client: InferenceClient,
    model: str,
    regime: str,
    states: list[EconomyState],
    max_retries: int,
    sleep_seconds: float,
) -> str:
    prompt = build_teacher_prompt(regime, states)

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=512,
            )
            return completion.choices[0].message.content
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(
                f"Teacher call failed for regime={regime} attempt={attempt}/{max_retries}: {exc}",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)

    raise RuntimeError(f"Teacher call failed after {max_retries} attempts: {last_error}")


def process_batch(
    client: InferenceClient,
    model: str,
    regime: str,
    states: list[EconomyState],
    max_retries: int,
    sleep_seconds: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    response_text = call_teacher(
        client=client,
        model=model,
        regime=regime,
        states=states,
        max_retries=max_retries,
        sleep_seconds=sleep_seconds,
    )

    labels = normalize_teacher_labels(response_text, regime)
    labels_by_id = {label.example_id: label for label in labels}

    raw_rows = []
    accepted_rows = []
    rejected_rows = []

    for state in states:
        state_data = asdict(state)
        label = labels_by_id.get(state.example_id)

        raw_rows.append(
            {
                "source": "teacher_guided",
                "teacher_model": model,
                "state": state_data,
                "teacher_response": response_text,
            }
        )

        if label is None:
            rejected_rows.append(
                {
                    "source": "teacher_guided",
                    "teacher_model": model,
                    "state": state_data,
                    "action": None,
                    "rejection_reason": "missing_label_for_example_id",
                }
            )
            continue

        reason = validation_reason(state, label.action)
        output_row = {
            "source": "teacher_guided",
            "teacher_model": model,
            "regime": regime,
            "state": state_data,
            "action": label.action,
        }

        if reason is None:
            accepted_rows.append(output_row)
        else:
            rejected_rows.append({**output_row, "rejection_reason": reason})

    return raw_rows, accepted_rows, rejected_rows


def generate_for_regime(
    client: InferenceClient,
    model: str,
    regime: str,
    examples_per_regime: int,
    batch_size: int,
    seed: int,
    max_candidates: int,
    max_retries: int,
    sleep_seconds: float,
    reset_files: bool,
) -> None:
    paths = output_paths(regime)
    if reset_files:
        for path in paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")

    rng = random.Random(seed + REGIMES.index(regime))
    accepted_count = 0
    rejected_count = 0
    raw_count = 0
    candidate_index = 0

    print("=" * 80)
    print(f"Generating teacher-guided labels for regime: {regime}")
    print(f"Target accepted examples: {examples_per_regime}")

    while accepted_count < examples_per_regime and candidate_index < max_candidates:
        states = []
        for _ in range(batch_size):
            candidate_index += 1
            states.append(make_state(regime, candidate_index, rng))

        raw_rows, accepted_rows, rejected_rows = process_batch(
            client=client,
            model=model,
            regime=regime,
            states=states,
            max_retries=max_retries,
            sleep_seconds=sleep_seconds,
        )

        needed = examples_per_regime - accepted_count
        accepted_to_write = accepted_rows[:needed]

        write_jsonl(paths["raw"], raw_rows, append=True)
        write_jsonl(paths["accepted"], accepted_to_write, append=True)
        write_jsonl(paths["rejected"], rejected_rows, append=True)

        raw_count += len(raw_rows)
        accepted_count += len(accepted_to_write)
        rejected_count += len(rejected_rows)

        print(
            f"{regime}: accepted={accepted_count}/{examples_per_regime} "
            f"rejected={rejected_count} raw={raw_count}"
        )

    if accepted_count < examples_per_regime:
        raise RuntimeError(
            f"Could only generate {accepted_count}/{examples_per_regime} accepted examples "
            f"for regime={regime}. Increase --max-candidates or loosen validators."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate teacher-guided fine-tune decision labels."
    )
    parser.add_argument(
        "--regimes",
        nargs="+",
        default=REGIMES,
        choices=REGIMES,
        help="Behavior regimes to generate.",
    )
    parser.add_argument(
        "--examples-per-regime",
        type=int,
        default=10,
        help="Accepted examples to generate per regime.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Candidate states per teacher call.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for synthetic state generation.",
    )
    parser.add_argument(
        "--model",
        default=MODEL_ID,
        help="HF Inference Provider model string.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=500,
        help="Maximum candidate states per regime before failing.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Teacher API retries per batch.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=2.0,
        help="Sleep duration after failed teacher calls.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing JSONL files instead of resetting them first.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN is not set.")
        print('Run: export HF_TOKEN="hf_your_token_here"')
        sys.exit(1)

    client = InferenceClient(token=hf_token)

    for regime in args.regimes:
        generate_for_regime(
            client=client,
            model=args.model,
            regime=regime,
            examples_per_regime=args.examples_per_regime,
            batch_size=args.batch_size,
            seed=args.seed,
            max_candidates=args.max_candidates,
            max_retries=args.max_retries,
            sleep_seconds=args.sleep_seconds,
            reset_files=not args.append,
        )

    print("=" * 80)
    print("Done. Outputs written under:", DATA_ROOT)


if __name__ == "__main__":
    main()
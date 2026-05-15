#!/usr/bin/env python3
"""
Probe a fine-tuned MLX-LM LoRA adapter on real validation examples.

This is a lightweight behavioral smoke/evaluation script.

It samples labeled examples from data/lora/<regime>/valid.jsonl, runs adapter-backed
MLX generation, normalizes the generated output to gather/work, and reports a
small accuracy/confusion summary.

It is intentionally small because Qwen3-8B generation is slow on local hardware.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MODEL = "Qwen/Qwen3-8B"
DEFAULT_REGIME = "survival"
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "lora" / DEFAULT_REGIME / "valid.jsonl"
DEFAULT_ADAPTER_PATH = PROJECT_ROOT / "adapters" / "qwen3_8b_survival"
ACTIONS = {"gather", "work"}


@dataclass(frozen=True)
class ProbeExample:
    example_id: str
    expected: str
    prompt: str


@dataclass(frozen=True)
class ProbeResult:
    example_id: str
    expected: str
    predicted: str
    raw_output: str
    correct: bool


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


def extract_expected_action(row: dict[str, Any]) -> str:
    metadata = row.get("metadata", {})
    action = str(metadata.get("action", "")).strip().lower()

    if not action:
        messages = row.get("messages", [])
        if messages:
            action = str(messages[-1].get("content", "")).strip().lower()

    if action not in ACTIONS:
        raise ValueError(f"Invalid expected action: {action!r}")

    return action


def extract_example_id(row: dict[str, Any], fallback_index: int) -> str:
    metadata = row.get("metadata", {})
    example_id = metadata.get("example_id")
    if example_id:
        return str(example_id)
    return f"valid_{fallback_index:05d}"


def build_prompt_from_messages(row: dict[str, Any]) -> str:
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError("Expected chat-style row with at least system and user messages.")

    system_content = str(messages[0].get("content", "")).strip()
    user_content = str(messages[1].get("content", "")).strip()

    # Add stricter inference-only formatting constraints. Qwen3 may otherwise emit
    # a <think> block before the final answer.
    return f"""{system_content}

Do not think step by step.
Do not explain.
Do not output <think> tags.
Return only one word: gather or work.

{user_content}

Return only one word: gather or work."""


def select_examples(rows: list[dict[str, Any]], samples_per_action: int, seed: int) -> list[ProbeExample]:
    grouped: dict[str, list[ProbeExample]] = {"gather": [], "work": []}

    for index, row in enumerate(rows, start=1):
        expected = extract_expected_action(row)
        grouped[expected].append(
            ProbeExample(
                example_id=extract_example_id(row, index),
                expected=expected,
                prompt=build_prompt_from_messages(row),
            )
        )

    rng = random.Random(seed)
    selected: list[ProbeExample] = []

    for action in ["gather", "work"]:
        candidates = list(grouped[action])
        rng.shuffle(candidates)
        selected.extend(candidates[:samples_per_action])

    rng.shuffle(selected)
    return selected


def run_generate(model: str, adapter_path: Path, prompt: str, max_tokens: int) -> str:
    command = [
        sys.executable,
        "-m",
        "mlx_lm",
        "generate",
        "--model",
        model,
        "--adapter-path",
        str(adapter_path),
        "--prompt",
        prompt,
        "--max-tokens",
        str(max_tokens),
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    output = "\n".join(part for part in [result.stdout, result.stderr] if part.strip())

    if result.returncode != 0:
        raise RuntimeError(
            "mlx_lm generate failed.\n"
            f"Command: {' '.join(command)}\n"
            f"Output:\n{output}"
        )

    return output.strip()


def extract_generated_text(raw_output: str) -> str:
    """Extract the model completion from mlx_lm generate output."""
    match = re.search(r"={5,}\n(?P<body>.*?)\n={5,}", raw_output, flags=re.DOTALL)
    if match:
        return match.group("body").strip()
    return raw_output.strip()


def normalize_output(raw_output: str) -> str:
    generated = extract_generated_text(raw_output).lower()

    # Remove Qwen-style thinking blocks if present.
    generated = re.sub(r"<think>.*?</think>", " ", generated, flags=re.DOTALL)

    tokens = re.findall(r"\b(?:gather|work)\b", generated)
    unique = set(tokens)

    if len(unique) == 1:
        return tokens[-1]
    if len(unique) > 1:
        return "ambiguous_gather_and_work"
    return "unknown"


def run_probe(args: argparse.Namespace) -> list[ProbeResult]:
    data_path = Path(args.data)
    adapter_path = Path(args.adapter_path)

    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter path not found: {adapter_path}")

    rows = read_jsonl(data_path)
    examples = select_examples(
        rows=rows,
        samples_per_action=args.samples_per_action,
        seed=args.seed,
    )

    if not examples:
        raise RuntimeError("No probe examples selected.")

    print("=" * 80)
    print("Fine-tuned LoRA validation probe")
    print(f"Model: {args.model}")
    print(f"Adapter: {adapter_path}")
    print(f"Data: {data_path}")
    print(f"Examples: {len(examples)}")

    results: list[ProbeResult] = []

    for probe_index, example in enumerate(examples, start=1):
        print("=" * 80)
        print(f"Probe {probe_index}/{len(examples)}")
        print(f"Example ID: {example.example_id}")
        print(f"Expected: {example.expected}")

        raw_output = run_generate(
            model=args.model,
            adapter_path=adapter_path,
            prompt=example.prompt,
            max_tokens=args.max_tokens,
        )
        predicted = normalize_output(raw_output)
        correct = predicted == example.expected

        print(f"Predicted: {predicted}")
        print(f"Correct: {correct}")
        if args.show_raw:
            print("Raw output:")
            print(raw_output)

        results.append(
            ProbeResult(
                example_id=example.example_id,
                expected=example.expected,
                predicted=predicted,
                raw_output=raw_output,
                correct=correct,
            )
        )

    return results


def print_summary(results: list[ProbeResult]) -> None:
    total = len(results)
    correct = sum(result.correct for result in results)
    accuracy = correct / total if total else 0.0

    expected_counts = Counter(result.expected for result in results)
    predicted_counts = Counter(result.predicted for result in results)
    confusion = Counter((result.expected, result.predicted) for result in results)

    print("=" * 80)
    print("Summary")
    print(f"Total: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Expected counts: {dict(expected_counts)}")
    print(f"Predicted counts: {dict(predicted_counts)}")
    print("Confusion:")
    for key, count in sorted(confusion.items()):
        expected, predicted = key
        print(f"  expected={expected:<6} predicted={predicted:<26} count={count}")

    print("=" * 80)
    print("Note: This is a small validation probe, not the final policy evaluation.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe a fine-tuned LoRA adapter on validation JSONL examples.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Base model or local model path.")
    parser.add_argument(
        "--adapter-path",
        default=str(DEFAULT_ADAPTER_PATH),
        help="Path to the saved LoRA adapter directory.",
    )
    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA_PATH),
        help="Path to a LoRA valid.jsonl file.",
    )
    parser.add_argument(
        "--samples-per-action",
        type=int,
        default=3,
        help="Number of gather and work examples to sample.",
    )
    parser.add_argument("--max-tokens", type=int, default=32, help="Maximum generated tokens.")
    parser.add_argument("--seed", type=int, default=42, help="Sampling seed.")
    parser.add_argument("--show-raw", action="store_true", help="Print raw mlx_lm output for each probe.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_probe(args)
    print_summary(results)


if __name__ == "__main__":
    main()
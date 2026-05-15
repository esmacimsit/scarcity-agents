#!/usr/bin/env python3
"""
Smoke-test fine-tuned LoRA adapter inference for the AI Society project.

This script checks whether a saved MLX-LM LoRA adapter can be loaded with the
final Qwen3-8B base model and used for small gather/work decision probes.

It is intentionally an adapter inference smoke test, not a final policy-quality
evaluation suite.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "Qwen/Qwen3-8B"
DEFAULT_ADAPTER_PATH = PROJECT_ROOT / "adapters" / "qwen3_8b_survival"


@dataclass(frozen=True)
class SmokeCase:
    name: str
    expected_hint: str
    prompt: str


SMOKE_CASES = [
    SmokeCase(
        name="critical_food_survival_should_gather",
        expected_hint="gather",
        prompt="""You are an agent in a scarcity-based economy simulation. Follow the survival regime. Prioritize long-term personal survival. Choose gather when food is low or scarcity is dangerous. Choose work when food is safe and coin is needed.

Do not think step by step.
Do not explain.
Do not output <think> tags.
Return only one word: gather or work.

Economy state:
- timestep: 12
- food: 0.8
- coin: 5.0
- productivity: 1.1
- wealth: 9.0
- food_price: 7.0
- alive_count: 30
- dead_total: 10
- total_food: 80.0
- scarcity_ratio: 2.5

Return only one word: gather or work.""",
    ),
    SmokeCase(
        name="safe_food_low_coin_survival_should_work",
        expected_hint="work",
        prompt="""You are an agent in a scarcity-based economy simulation. Follow the survival regime. Prioritize long-term personal survival. Choose gather when food is low or scarcity is dangerous. Choose work when food is safe and coin is needed.

Do not think step by step.
Do not explain.
Do not output <think> tags.
Return only one word: gather or work.

Economy state:
- timestep: 20
- food: 10.5
- coin: 0.4
- productivity: 1.2
- wealth: 12.0
- food_price: 1.1
- alive_count: 45
- dead_total: 1
- total_food: 250.0
- scarcity_ratio: 0.7

Return only one word: gather or work.""",
    ),
]


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


def normalize_output(text: str) -> str:
    lowered = text.lower()
    if "gather" in lowered and "work" not in lowered:
        return "gather"
    if "work" in lowered and "gather" not in lowered:
        return "work"
    if "gather" in lowered and "work" in lowered:
        # For smoke testing, keep this visible rather than hiding ambiguity.
        return "ambiguous_gather_and_work"
    return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run smoke inference with a fine-tuned MLX-LM LoRA adapter.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Base model or local model path.")
    parser.add_argument(
        "--adapter-path",
        default=str(DEFAULT_ADAPTER_PATH),
        help="Path to the saved LoRA adapter directory.",
    )
    parser.add_argument("--max-tokens", type=int, default=32, help="Maximum generated tokens.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter_path = Path(args.adapter_path)

    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter path not found: {adapter_path}")

    print("=" * 80)
    print("Fine-tuned LoRA inference smoke test")
    print(f"Model: {args.model}")
    print(f"Adapter: {adapter_path}")

    for case in SMOKE_CASES:
        print("=" * 80)
        print(f"Case: {case.name}")
        print(f"Expected hint: {case.expected_hint}")

        output = run_generate(
            model=args.model,
            adapter_path=adapter_path,
            prompt=case.prompt,
            max_tokens=args.max_tokens,
        )
        normalized = normalize_output(output)

        print("Raw output:")
        print(output)
        print(f"Normalized output: {normalized}")

    print("=" * 80)
    print("Done. This smoke test verifies fine-tuned adapter load/generation and provides lightweight behavioral probes.")


if __name__ == "__main__":
    main()


"""
Runtime wrapper for fine-tuned Qwen3-8B LoRA policy adapters.

This module is intentionally small and conservative:
- select the adapter path for a regime
- build the prompt from the simulation state
- call MLX-LM generation
- normalize the output to gather/work

The selected adapters are documented in analysis/finetuned_adapter_selection.md.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from policies.prompt_builders import build_fine_tuned_policy_prompt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "Qwen/Qwen3-8B"
VALID_ACTIONS = {"gather", "work"}

SELECTED_ADAPTERS: dict[str, Path] = {
    "survival": PROJECT_ROOT / "adapters" / "qwen3_8b_survival_v2",
    "social_welfare": PROJECT_ROOT / "adapters" / "qwen3_8b_social_welfare",
    "wealth_maximizing": PROJECT_ROOT / "adapters" / "qwen3_8b_wealth_maximizing_v2",
}


@dataclass(frozen=True)
class FineTunedPolicyResult:
    regime: str
    action: str
    raw_output: str
    adapter_path: Path


class FineTunedPolicyError(RuntimeError):
    """Raised when a fine-tuned adapter cannot produce a valid action."""


def extract_generated_text(raw_output: str) -> str:
    """Extract the generated body from mlx_lm generate output."""
    match = re.search(r"={5,}\n(?P<body>.*?)\n={5,}", raw_output, flags=re.DOTALL)
    if match:
        return match.group("body").strip()
    return raw_output.strip()


def normalize_action(raw_output: str) -> str:
    """Normalize MLX/Qwen output into exactly gather or work."""
    generated = extract_generated_text(raw_output).lower()
    generated = re.sub(r"<think>.*?</think>", " ", generated, flags=re.DOTALL)

    tokens = re.findall(r"\b(?:gather|work)\b", generated)
    unique = set(tokens)

    if len(unique) == 1:
        return tokens[-1]

    raise FineTunedPolicyError(f"Could not normalize fine-tuned output to one action: {generated!r}")


def run_mlx_generate(
    *,
    model: str,
    adapter_path: Path,
    prompt: str,
    max_tokens: int,
) -> str:
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
        raise FineTunedPolicyError(
            "mlx_lm generate failed.\n"
            f"Adapter: {adapter_path}\n"
            f"Output:\n{output}"
        )

    return output.strip()


def choose_fine_tuned_action(
    regime: str,
    state: Mapping[str, Any],
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 32,
) -> FineTunedPolicyResult:
    """Choose gather/work using the selected fine-tuned adapter for a regime."""
    if regime not in SELECTED_ADAPTERS:
        valid = ", ".join(sorted(SELECTED_ADAPTERS))
        raise ValueError(f"Unknown fine-tuned regime: {regime!r}. Expected one of: {valid}")

    adapter_path = SELECTED_ADAPTERS[regime]
    if not adapter_path.exists():
        raise FileNotFoundError(f"Selected adapter path not found: {adapter_path}")

    prompt = build_fine_tuned_policy_prompt(regime=regime, state=state)
    raw_output = run_mlx_generate(
        model=model,
        adapter_path=adapter_path,
        prompt=prompt,
        max_tokens=max_tokens,
    )
    action = normalize_action(raw_output)

    return FineTunedPolicyResult(
        regime=regime,
        action=action,
        raw_output=raw_output,
        adapter_path=adapter_path,
    )


def choose_action(regime: str, state: Mapping[str, Any]) -> str:
    """Small convenience wrapper for simulation code that only needs the action."""
    return choose_fine_tuned_action(regime=regime, state=state).action
#!/usr/bin/env python3
"""
Runtime smoke test for selected fine-tuned policy adapters.

This test verifies that the runtime policy wrapper can:
- import the selected fine-tuned policy module
- build prompts from simulation-like states
- load the selected adapter for each regime
- call MLX-LM generation
- normalize outputs into gather/work

This is not the final simulation-level policy evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from policies.finetuned import FineTunedPolicyError, choose_fine_tuned_action


REGIMES = ["survival", "social_welfare", "wealth_maximizing"]


@dataclass(frozen=True)
class RuntimeSmokeCase:
    name: str
    state: dict[str, Any]
    expected_hints: dict[str, str]
    note: str


SMOKE_CASES = [
    RuntimeSmokeCase(
        name="borderline_risk_state",
        state={
            "timestep": 12,
            "food": 2.5,
            "coin": 1.0,
            "productivity": 1.1,
            "wealth": 12.8,
            "food_price": 4.7,
            "alive_count": 35,
            "dead_total": 8,
            "total_food": 120.0,
            "scarcity_ratio": 2.1,
        },
        expected_hints={
            "survival": "gather",
            "social_welfare": "gather",
            "wealth_maximizing": "gather_or_work",
        },
        note="Borderline wealth-risk case. Survival/social should gather; wealth may still choose work.",
    ),
    RuntimeSmokeCase(
        name="critical_personal_survival_risk_state",
        state={
            "timestep": 40,
            "food": 1.2,
            "coin": 0.5,
            "productivity": 1.0,
            "wealth": 6.0,
            "food_price": 6.5,
            "alive_count": 30,
            "dead_total": 15,
            "total_food": 70.0,
            "scarcity_ratio": 2.8,
        },
        expected_hints={
            "survival": "gather",
            "social_welfare": "gather",
            "wealth_maximizing": "gather",
        },
        note="Critical risk case. All regimes should be able to choose gather.",
    ),
    RuntimeSmokeCase(
        name="safe_wealth_work_state",
        state={
            "timestep": 20,
            "food": 10.5,
            "coin": 1.0,
            "productivity": 1.2,
            "wealth": 14.0,
            "food_price": 1.2,
            "alive_count": 48,
            "dead_total": 1,
            "total_food": 260.0,
            "scarcity_ratio": 0.7,
        },
        expected_hints={
            "survival": "work",
            "social_welfare": "work",
            "wealth_maximizing": "work",
        },
        note="Safe low-scarcity case. Work is expected for all regimes.",
    ),
]


def hint_matches(expected_hint: str, actual_action: str) -> bool:
    if expected_hint == "gather_or_work":
        return actual_action in {"gather", "work"}
    return actual_action == expected_hint


def main() -> None:
    print("=" * 80)
    print("Fine-tuned policy runtime smoke test")
    print("Regimes:", ", ".join(REGIMES))

    total = 0
    matched = 0
    hard_failures = 0

    for case in SMOKE_CASES:
        print("=" * 80)
        print(f"Case: {case.name}")
        print(f"Note: {case.note}")

        for regime in REGIMES:
            total += 1
            expected_hint = case.expected_hints[regime]

            try:
                result = choose_fine_tuned_action(regime=regime, state=case.state)
                ok = hint_matches(expected_hint, result.action)
                matched += int(ok)

                print(
                    f"regime={regime:<18} "
                    f"action={result.action:<6} "
                    f"expected_hint={expected_hint:<14} "
                    f"match={ok} "
                    f"adapter={result.adapter_path.name}"
                )
            except (FineTunedPolicyError, FileNotFoundError, ValueError) as exc:
                hard_failures += 1
                print(
                    f"regime={regime:<18} "
                    f"ERROR={type(exc).__name__}: {exc}"
                )

    print("=" * 80)
    print("Summary")
    print(f"Total checks: {total}")
    print(f"Hint matches: {matched}/{total}")
    print(f"Hard failures: {hard_failures}")

    if hard_failures:
        raise SystemExit(1)

    print("Runtime smoke status: PASS")
    print("Note: Hint mismatches are behavioral signals, not infrastructure failures.")


if __name__ == "__main__":
    main()

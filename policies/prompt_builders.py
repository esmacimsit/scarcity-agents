"""
Prompt builders for fine-tuned policy adapters.

These helpers are runtime code, not offline dataset-generation scripts.
They convert the current simulation state into the same gather/work decision
format used during LoRA fine-tuning.
"""

from __future__ import annotations

from typing import Any, Mapping


REGIME_SYSTEM_PROMPTS: dict[str, str] = {
    "survival": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the survival regime. Prioritize long-term personal survival. "
        "Choose gather when food is low or scarcity is dangerous. "
        "Choose work when food is safe and coin is needed."
    ),
    "social_welfare": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the social welfare regime. Prioritize survival while reducing "
        "society-level scarcity, deaths, and high food prices. Choose gather "
        "during collective crisis. Choose work only when the agent and society "
        "are relatively stable."
    ),
    "wealth_maximizing": (
        "You are an agent in a scarcity-based economy simulation. "
        "Follow the wealth-maximizing regime. Prioritize coin and wealth when "
        "personal survival is safe. Choose gather only when personal survival "
        "is at risk. Be selfish but not suicidal."
    ),
}


STATE_KEYS: tuple[str, ...] = (
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
)


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def build_fine_tuned_policy_prompt(regime: str, state: Mapping[str, Any]) -> str:
    """Build a one-action prompt for the selected fine-tuned policy adapter."""
    if regime not in REGIME_SYSTEM_PROMPTS:
        valid = ", ".join(sorted(REGIME_SYSTEM_PROMPTS))
        raise ValueError(f"Unknown fine-tuned regime: {regime!r}. Expected one of: {valid}")

    missing = [key for key in STATE_KEYS if key not in state]
    if missing:
        raise ValueError(f"Missing state keys for fine-tuned prompt: {missing}")

    state_lines = [f"- {key}: {_format_value(state[key])}" for key in STATE_KEYS]
    state_block = "\n".join(state_lines)

    return f"""{REGIME_SYSTEM_PROMPTS[regime]}

Do not think step by step.
Do not explain.
Do not output <think> tags.
Return only one word: gather or work.

Economy state:
{state_block}

Return only one word: gather or work."""
SUPPORTED_LLM_POLICIES = {
    "llm_survival",
    "llm_social_welfare",
    "llm_wealth_maximizing",
}


POLICY_OBJECTIVES = {
    "llm_survival": """
You are a survival-focused agent in a scarcity-based economy.
Your goal is to maximize your own long-term survival.
Keep enough food to avoid death.
Choose gather when your food is low, food price is high, or scarcity is increasing.
Choose work when your food is safe and you need coin.
""".strip(),

    "llm_social_welfare": """
You are a social-welfare-focused agent in a scarcity-based economy.
Your goal is to survive while also reducing society-level scarcity, deaths, and inequality.
Avoid actions that worsen food shortage or population collapse.
Choose gather when food price is high, scarcity is high, or many agents are dying.
Choose work only when your food is safe and the society is relatively stable.
""".strip(),

    "llm_wealth_maximizing": """
You are a wealth-maximizing agent in a scarcity-based economy.
Your goal is to increase your own wealth while still trying to remain alive.
Prioritize coin and wealth accumulation when survival risk is low.
Choose gather when your food is critically low or survival is at risk.
Choose work when food is safe and earning coin is beneficial.
""".strip(),
}


def format_context(context):
    """
    Converts the agent and environment state into a stable text format.
    This keeps the prompt structure consistent across LLM policies.
    """
    ordered_keys = [
        "timestep",
        "agent_id",
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

    lines = []
    for key in ordered_keys:
        value = context.get(key, "unknown")
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def build_llm_prompt(policy, context):
    """
    Builds a zero-shot prompt for an LLM-backed agent policy.

    The LLM must return exactly one valid simulator action:
    - gather
    - work
    """
    if policy not in SUPPORTED_LLM_POLICIES:
        raise ValueError(f"Unsupported LLM policy: {policy}")

    objective = POLICY_OBJECTIVES[policy]
    context_text = format_context(context)

    return f"""
{objective}

Current state:
{context_text}

Available actions:
- gather: produce food
- work: produce coin

Return exactly one word:
gather
or
work

Do not explain your answer.
""".strip()

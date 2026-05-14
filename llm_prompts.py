SUPPORTED_LLM_POLICIES = {
    "llm_survival",
    "llm_social_welfare",
    "llm_wealth_maximizing",
}


# Few-shot policy mapping and support
FEW_SHOT_POLICY_MAP = {
    "llm_survival_few_shot": "llm_survival",
    "llm_social_welfare_few_shot": "llm_social_welfare",
    "llm_wealth_maximizing_few_shot": "llm_wealth_maximizing",
}

SUPPORTED_FEW_SHOT_POLICIES = set(FEW_SHOT_POLICY_MAP.keys())


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


# Few-shot example blocks for each policy
FEW_SHOT_EXAMPLES = {
    "llm_survival_few_shot": [
        {
            "state": {
                "food": 1.0,
                "coin": 5.0,
                "food_price": 5.5,
                "scarcity_ratio": 2.0,
            },
            "action": "gather",
            "reason": "Food is critically low and price is high, so survival requires producing food.",
        },
        {
            "state": {
                "food": 9.0,
                "coin": 0.5,
                "food_price": 1.2,
                "scarcity_ratio": 0.9,
            },
            "action": "work",
            "reason": "Food is safe and price is low, so the agent can earn coin.",
        },
        {
            "state": {
                "food": 4.0,
                "coin": 4.0,
                "food_price": 4.5,
                "scarcity_ratio": 1.8,
            },
            "action": "gather",
            "reason": "Food is not yet critical, but scarcity and price are high, so gathering reduces survival risk.",
        },
    ],
    "llm_social_welfare_few_shot": [
        {
            "state": {
                "food": 3.0,
                "coin": 6.0,
                "food_price": 6.0,
                "alive_count": 30,
                "dead_total": 20,
                "scarcity_ratio": 2.3,
            },
            "action": "gather",
            "reason": "Scarcity, price, and deaths are high, so producing food protects the society.",
        },
        {
            "state": {
                "food": 8.0,
                "coin": 2.0,
                "food_price": 1.0,
                "alive_count": 50,
                "dead_total": 0,
                "scarcity_ratio": 0.8,
            },
            "action": "work",
            "reason": "The society is stable and food is safe, so working is acceptable.",
        },
        {
            "state": {
                "food": 5.0,
                "coin": 5.0,
                "food_price": 4.0,
                "alive_count": 35,
                "dead_total": 15,
                "scarcity_ratio": 1.7,
            },
            "action": "gather",
            "reason": "Deaths and scarcity are already visible, so the society needs more food production.",
        },
    ],
    "llm_wealth_maximizing_few_shot": [
        {
            "state": {
                "food": 10.0,
                "coin": 0.5,
                "food_price": 1.0,
                "scarcity_ratio": 0.8,
            },
            "action": "work",
            "reason": "Food is safe and cheap, so earning coin increases wealth.",
        },
        {
            "state": {
                "food": 1.0,
                "coin": 10.0,
                "food_price": 6.0,
                "scarcity_ratio": 2.1,
            },
            "action": "gather",
            "reason": "Food is critical; the agent must survive before wealth can matter.",
        },
        {
            "state": {
                "food": 6.0,
                "coin": 2.0,
                "food_price": 2.0,
                "scarcity_ratio": 1.0,
            },
            "action": "work",
            "reason": "Food is acceptable and scarcity is not high, so working supports wealth growth.",
        },
    ],
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


def format_example(example):
    """
    Formats a few-shot example into a compact state/action block.
    """
    state_lines = []
    for key, value in example["state"].items():
        state_lines.append(f"{key}: {value}")

    state_text = "\n".join(state_lines)

    return f"""
State:
{state_text}
Action: {example["action"]}
Reason: {example["reason"]}
""".strip()


def format_few_shot_examples(policy):
    """
    Formats the objective-specific examples used by few-shot policies.
    """
    examples = FEW_SHOT_EXAMPLES[policy]
    formatted_examples = []

    for index, example in enumerate(examples, start=1):
        formatted_examples.append(f"Example {index}:\n{format_example(example)}")

    return "\n\n".join(formatted_examples)


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


# Few-shot prompt builder for LLM policies
def build_few_shot_prompt(policy, context):
    """
    Builds a few-shot prompt for an LLM-backed agent policy.

    Few-shot policies include a small number of objective-specific
    state/action examples before the current decision state.
    """
    if policy not in SUPPORTED_FEW_SHOT_POLICIES:
        raise ValueError(f"Unsupported few-shot LLM policy: {policy}")

    base_policy = FEW_SHOT_POLICY_MAP[policy]
    objective = POLICY_OBJECTIVES[base_policy]
    examples_text = format_few_shot_examples(policy)
    context_text = format_context(context)

    return f"""
{objective}

The following examples show how this objective should be applied.
They are examples, not hard rules.

{examples_text}

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

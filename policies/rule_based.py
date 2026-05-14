def decide_rule_action(context, rng, cfg):
    """
    Deterministic non-LLM baseline policy.

    This policy uses hand-written scarcity-aware rules.
    It is used as a strong baseline against random and LLM-based policies.
    """
    food = context["food"]
    coin = context["coin"]
    food_price = context["food_price"]
    base_price = cfg["base_price"]

    if food < 2.0:
        return "gather"

    if coin < food_price:
        return "work"

    if food_price > base_price * 1.5 and food < 5.0:
        return "gather"

    if food > 8.0 and coin < 10.0:
        return "work"

    return rng.choice(["gather", "work"])
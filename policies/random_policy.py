def decide_random_action(rng):
    """
    Stochastic baseline policy.

    This policy ignores all agent and environment state.
    It is used as the no-strategy baseline.
    """
    return rng.choice(["gather", "work"])
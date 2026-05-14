from policies.random_policy import decide_random_action
from policies.rule_based import decide_rule_action
from policies.zero_shot import ZERO_SHOT_LLM_POLICIES, decide_zero_shot_action


SUPPORTED_POLICIES = {
    "random",
    "rule",
    *ZERO_SHOT_LLM_POLICIES,
}


def decide_policy_action(policy, context, rng, cfg):
    """
    Routes a policy name to the correct decision strategy.

    The simulation engine calls this function instead of knowing the
    implementation details of each policy.
    """
    if policy == "random":
        return decide_random_action(rng)

    if policy == "rule":
        return decide_rule_action(context=context, rng=rng, cfg=cfg)

    if policy in ZERO_SHOT_LLM_POLICIES:
        return decide_zero_shot_action(policy=policy, context=context)

    raise ValueError(f"Unknown policy: {policy}")


__all__ = [
    "SUPPORTED_POLICIES",
    "decide_policy_action",
]
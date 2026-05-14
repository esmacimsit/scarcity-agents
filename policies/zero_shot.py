from llm_client import decide_with_llm
from llm_prompts import build_llm_prompt


ZERO_SHOT_LLM_POLICIES = {
    "llm_survival",
    "llm_social_welfare",
    "llm_wealth_maximizing",
}


def decide_zero_shot_action(policy, context, model=None):
    """
    Zero-shot LLM policy.

    This function builds an objective-specific prompt from the current
    decision context and asks the local LLM to choose one simulator action.

    No example state/action pairs are included here, so this remains zero-shot.
    """
    if policy not in ZERO_SHOT_LLM_POLICIES:
        raise ValueError(f"Unsupported zero-shot LLM policy: {policy}")

    prompt = build_llm_prompt(policy=policy, context=context)

    if model is None:
        return decide_with_llm(prompt)

    return decide_with_llm(prompt, model=model)
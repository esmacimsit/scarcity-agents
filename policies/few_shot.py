from llm_client import decide_with_llm
from llm_prompts import SUPPORTED_FEW_SHOT_POLICIES, build_few_shot_prompt


FEW_SHOT_LLM_POLICIES = SUPPORTED_FEW_SHOT_POLICIES


def decide_few_shot_action(policy, context, model=None):
    """
    Few-shot LLM policy.

    This function builds an objective-specific few-shot prompt from the current
    decision context and asks the local LLM to choose one simulator action.

    Unlike zero-shot prompting, this policy includes a small number of
    state/action examples before the current state.
    """
    if policy not in FEW_SHOT_LLM_POLICIES:
        raise ValueError(f"Unsupported few-shot LLM policy: {policy}")

    prompt = build_few_shot_prompt(policy=policy, context=context)

    if model is None:
        return decide_with_llm(prompt)

    return decide_with_llm(prompt, model=model)
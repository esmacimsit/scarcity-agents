import json
import urllib.error
import urllib.request


DEFAULT_MODEL = "qwen3:8b"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
VALID_ACTIONS = {"gather", "work"}
FALLBACK_ACTION = "gather"

STRICT_ACTION_INSTRUCTION = """
You are controlling one simulator agent.
This is a zero-shot decision task, not a chat task.
Do not explain, reason, or describe alternatives.
Return only one valid action token: gather or work.
""".strip()


def parse_llm_action(raw_response):
    """
    Converts raw LLM output into a valid simulator action.

    The simulator only accepts:
    - gather
    - work

    If the response is invalid or unclear, we use a survival-oriented fallback.
    """
    if raw_response is None:
        return FALLBACK_ACTION

    text = str(raw_response).strip().lower()

    if text in VALID_ACTIONS:
        return text

    # Handles responses like: "I choose gather." or "Action: work".
    # This keeps the simulator safe even if the model ignores strict formatting.
    tokens = (
        text.replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("\n", " ")
        .split()
    )

    for token in tokens:
        if token in VALID_ACTIONS:
            return token

    return FALLBACK_ACTION


def build_ollama_payload(prompt, model=DEFAULT_MODEL):
    """
    Builds a strict Ollama request payload.

    This remains zero-shot: no example state/action pairs are added.
    The extra instruction only constrains output format and action space.
    """
    strict_prompt = f"{STRICT_ACTION_INSTRUCTION}\n\n{prompt.strip()}"

    return {
        "model": model,
        "prompt": f"/no_think\n{strict_prompt}",
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_predict": 3,
            "top_p": 0.1,
        },
    }


def call_ollama(prompt, model=DEFAULT_MODEL, timeout=60):
    """
    Sends a prompt to Ollama and returns the raw response text.
    """
    payload = build_ollama_payload(prompt=prompt, model=model)
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_body = response.read().decode("utf-8")

    parsed = json.loads(response_body)
    return parsed.get("response", "")


def decide_with_llm(prompt, model=DEFAULT_MODEL):
    """
    Calls the local LLM and returns a valid simulator action.

    If Ollama is unavailable or the model returns an invalid response,
    the function safely falls back to gather.
    """
    try:
        raw_response = call_ollama(prompt=prompt, model=model)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        print(f"LLM call failed, using fallback action: {error}")
        return FALLBACK_ACTION

    return parse_llm_action(raw_response)


if __name__ == "__main__":
    test_prompt = """
Action meanings:
- gather = produce food
- work = produce coin

Current state:
food: 1.2
coin: 4.0
food_price: 5.8
scarcity_ratio: 2.1

Food is low and food price is high, so the agent should prioritize food production.
""".strip()

    action = decide_with_llm(test_prompt)
    print(action)
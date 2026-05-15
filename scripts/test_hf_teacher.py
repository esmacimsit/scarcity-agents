#!/usr/bin/env python3

import os
import sys
from huggingface_hub import InferenceClient


MODEL_ID = "Qwen/Qwen3-235B-A22B-Instruct-2507:novita"


def main() -> None:
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("ERROR: HF_TOKEN is not set.")
        print('Run: export HF_TOKEN="hf_your_token_here"')
        sys.exit(1)

    client = InferenceClient(token=hf_token)

    prompt = """You are labeling one training example for a scarcity-based economy simulation.

Behavior regime: wealth_maximizing

State:
food: 8.0
coin: 1.0
food_price: 2.0
scarcity_ratio: 1.1
alive_count: 50
dead_total: 0

Available actions:
- gather
- work

The wealth_maximizing regime is self-interested.
If personal food is safe, prefer work to increase coin/wealth.
If personal food is critical, choose gather.

Return exactly one word:
gather
or
work
"""

    completion = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=5,
        temperature=0.0,
    )

    answer = completion.choices[0].message.content.strip().lower()

    print("Model:", MODEL_ID)
    print("Answer:", answer)

    if answer not in {"gather", "work"}:
        print("WARNING: Answer is not a clean gather/work label.")


if __name__ == "__main__":
    main()
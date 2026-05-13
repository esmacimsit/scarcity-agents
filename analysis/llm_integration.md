# LLM Integration Plan

This document defines the plan for adding LLM-based decision policies to the scarcity-based agent society simulation.

Chapter 1 established the non-LLM baseline framework:

- `random` policy
- `rule` policy
- `default`, `moderate_scarcity`, and `scarcity` scenarios
- multi-seed experiments
- summary metrics
- baseline comparison
- visualization pipeline

Chapter 2 extends this framework by introducing LLM-driven agents.

---

## Main Goal

The goal is to evaluate whether LLM-based agents can make meaningful decisions under scarcity without relying on hard-coded rules.

The core research question is:

> How do different LLM decision objectives affect survival, inequality, and market stability in a scarcity-based agent society?

The LLM is not used as a chatbot. It is used as a decision policy.

For each agent and timestep, the LLM receives the current decision context and returns exactly one action:

```text
gather
```

or:

```text
work
```

---

## Why Add LLM Policies?

The current `rule` policy works well because scarcity-aware behavior is manually encoded.

For example, the rule policy increases food production when food is low or food price is high.

The LLM experiment asks a different question:

> Can a language model infer useful scarcity-aware behavior from the environment state and objective prompt?

This allows us to compare:

| Policy | Meaning |
|---|---|
| `random` | No reasoning or adaptation |
| `rule` | Manually written scarcity-aware behavior |
| LLM policies | Prompt-driven decision behavior |

The goal is not only to beat random behavior, but also to observe whether LLM agents can approach or differ meaningfully from the rule-based baseline.

---

## Model Choice

The initial model will be:

```text
Qwen2.5 7B
```

Reasoning:

- 7B is practical for local experimentation.
- It is lighter and faster than 14B.
- It is enough to test whether LLM-based decision policies are meaningful.
- Model size comparison is not the main focus of this project.

The main focus is objective design, not model scaling.

---

## LLM Policy Objectives

We will test three pure LLM society types.

Each run uses the same model, but a different objective prompt.

---

## 1. `llm_survival`

This policy represents a survival-focused agent.

Objective:

```text
Prioritize your own long-term survival.
Keep enough food to avoid death.
Work when food is safe and coin is needed.
```

Expected behavior:

- gather when food is low
- work when food is safe but coin is low
- react to scarcity mostly through individual survival needs

This is the middle-ground LLM objective.

---

## 2. `llm_social_welfare`

This policy represents a social-welfare-focused agent.

Objective:

```text
Survive, but also avoid worsening society-level scarcity, deaths, and inequality.
When scarcity or food price is high, prefer decisions that stabilize the population.
```

Expected behavior:

- gather more under scarcity
- avoid actions that intensify food shortage
- reduce deaths and price pressure if successful
- potentially produce lower inequality than survival-only behavior

This is the most cooperative/stability-oriented LLM objective.

---

## 3. `llm_wealth_maximizing`

This policy represents a self-interest or wealth-maximizing agent.

Objective:

```text
Prioritize increasing your own wealth while still trying to remain alive.
```

Expected behavior:

- may choose work more often when coin accumulation seems beneficial
- may be less sensitive to society-level scarcity
- may increase inequality or market instability under pressure

This is not described as an evil agent in the report. It is a self-interest baseline.

It helps test whether individual wealth-oriented behavior produces worse society-level outcomes under scarcity.

---

## Pure Society First

The first LLM experiments will use pure societies.

That means all agents in a run share the same LLM objective.

Examples:

```text
Run 1: 50 agents = llm_survival
Run 2: 50 agents = llm_social_welfare
Run 3: 50 agents = llm_wealth_maximizing
```

This makes the results easier to interpret.

We can directly compare what happens when the whole society follows one objective.

Mixed societies may be added later, but they are not part of the first LLM implementation.

---

## Future Mixed Society Extension

After pure societies work, we may introduce mixed societies.

Example:

```text
40% survival-focused agents
40% social-welfare-focused agents
20% wealth-maximizing agents
```

This would allow a more complex question:

> How does the composition of agent objectives affect survival, inequality, and market stability?

This is useful for the React UI because it could later support sliders for society composition.

However, this is a later extension. The first goal is pure LLM societies.

---

## Decision Context

The LLM receives the same decision context already produced by `World.build_decision_context()`.

Current context fields:

```text
timestep
agent_id
food
coin
productivity
wealth
food_price
alive_count
dead_total
total_food
scarcity_ratio
```

These fields describe both individual state and society-level scarcity.

The LLM must use this context to choose only one action:

```text
gather
```

or:

```text
work
```

---

## Prompting Strategy

Initial LLM experiments will be zero-shot.

Zero-shot means:

```text
No training.
No examples.
Only objective prompt + current state.
```

Later, few-shot prompting may be added.

Few-shot means:

```text
The prompt includes several example states and correct actions.
```

Fine-tuning is not part of the first LLM integration.

Fine-tuning may later be used to create a scarcity-aware or social-welfare-adapted model.

---

## Output Control

The LLM must return exactly one of:

```text
gather
work
```

The simulator will normalize the result.

If the LLM returns an invalid response, the system should safely fall back to:

```text
gather
```

This fallback is survival-oriented and prevents simulation crashes.

---

## Evaluation Metrics

LLM policies will be evaluated using the same Chapter 1 metrics:

- survival rate
- total deaths
- final alive agents
- average food price
- price volatility
- Gini survivor
- Gini population
- gather ratio
- work ratio
- average trades

The key comparison is:

```text
random vs rule vs llm_survival vs llm_social_welfare vs llm_wealth_maximizing
```

across:

```text
default
moderate_scarcity
scarcity
```

The most important scenario will likely be:

```text
moderate_scarcity
```

because it shows suffering and inequality without immediate total collapse.

---

## Expected Results

Expected high-level behavior:

| Policy | Expected Outcome |
|---|---|
| `random` | Fails under scarcity |
| `rule` | Strong stable baseline |
| `llm_survival` | Better than random if it detects individual risk |
| `llm_social_welfare` | Potentially more stable under scarcity |
| `llm_wealth_maximizing` | May increase inequality or price pressure |

The most interesting result would be:

> LLM objectives produce different society-level outcomes even when using the same underlying model.

This makes the LLM experiment more meaningful than simply adding one generic LLM policy.

---

## UI Meaning

The React UI can expose LLM policies as selectable decision modes:

```text
Random Policy
Rule-Based Policy
LLM Survival-Focused
LLM Social-Welfare-Focused
LLM Wealth-Maximizing
```

The dashboard can show:

- alive agents over time
- food price over time
- population Gini over time
- gather ratio over time
- agent grid
- selected agent state and decision

This makes the effect of different decision objectives visible.

The main UI story is:

> Select the same scarcity scenario, change the policy objective, and observe how the society changes.

---

## Implementation Phases

## CH2-001 — LLM Integration Plan

Status: planned in this document.

Purpose:

```text
Define LLM objectives, experiment scope, and evaluation logic.
```

---

## CH2-002 — Add LLM Policy Names

Add policy support for:

```text
llm_survival
llm_social_welfare
llm_wealth_maximizing
```

These should be recognized by `World.decide_action()`.

---

## CH2-003 — Add Prompt Builder

Create a prompt builder that generates objective-specific prompts.

Possible file:

```text
llm_prompts.py
```

It should contain prompt logic for:

```text
survival
social_welfare
wealth_maximizing
```

---

## CH2-004 — Add LLM Client

Create a local LLM client for Qwen2.5 7B.

Possible file:

```text
llm_client.py
```

Responsibilities:

- send prompt to model
- receive raw response
- parse action
- handle errors
- return `gather` or `work`

---

## CH2-005 — Connect LLM to World

Update `World.decide_llm_action()` so it calls the LLM client instead of returning random actions.

---

## CH2-006 — Run Smoke Test

Before full experiments, run a small test:

```text
n_agents = 5 or 10
timesteps = 10 or 30
scenario = moderate_scarcity
policy = llm_survival
seed = 1
```

Purpose:

- confirm LLM responds
- confirm output parsing works
- check runtime
- avoid wasting time on full experiments too early

---

## CH2-007 — Pure LLM Society Experiments

Run pure LLM societies:

```text
llm_survival
llm_social_welfare
llm_wealth_maximizing
```

Compare them against:

```text
random
rule
```

---

## CH2-008 — Optional Extensions

Possible later extensions:

- few-shot prompting
- fine-tuned social-welfare model
- mixed society composition
- React UI policy comparison dashboard

These should come after the pure LLM society experiments work reliably.

---

## Final Chapter 2 Direction

The first LLM milestone is not fine-tuning.

The first milestone is:

> Run the same Qwen2.5 7B model with three different objectives and measure how each objective changes society-level outcomes.

This keeps the project manageable, interpretable, and visually meaningful for the UI.
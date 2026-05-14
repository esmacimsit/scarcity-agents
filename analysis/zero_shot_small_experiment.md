# Zero-Shot LLM Small Experiment Results

This document records a small controlled comparison between baseline policies and zero-shot LLM policies.

This is not the final full-scale experiment. The purpose of this run is to observe early behavior patterns under equal conditions and confirm that the zero-shot LLM policies can be compared with the existing random and rule-based baselines.

---

## Experiment Setup

| Setting | Value |
|---|---|
| Model | `qwen3:8b` via Ollama |
| Prompting method | Zero-shot objective prompting |
| Agents | 10 |
| Timesteps | 30 |
| Seed | 1 |
| Scenarios | `default`, `moderate_scarcity`, `scarcity` |
| Baseline policies | `random`, `rule` |
| Zero-shot LLM policies | `llm_survival`, `llm_social_welfare`, `llm_wealth_maximizing` |

All policies were executed under the same scenario, seed, population size, and timestep settings.

---

## Policies Compared

| Policy | Type | Description |
|---|---|---|
| `random` | Baseline | Chooses `gather` or `work` randomly. |
| `rule` | Baseline | Uses hand-written scarcity-aware decision rules. |
| `llm_survival` | Zero-shot LLM | Optimizes individual long-term survival. |
| `llm_social_welfare` | Zero-shot LLM | Optimizes society-level stability, scarcity reduction, and lower inequality. |
| `llm_wealth_maximizing` | Zero-shot LLM | Optimizes individual wealth and coin accumulation. |

---

## Summary of Observed Results

### Default Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 1.00 | 0 | 1.9809 | 0.0789 | 0.5167 |
| `rule` | 1.00 | 0 | 1.9148 | 0.0645 | 0.4967 |
| `llm_survival` | 1.00 | 0 | 3.6463 | 0.0601 | 0.3933 |
| `llm_social_welfare` | 1.00 | 0 | 0.9386 | 0.0262 | 1.0000 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.5108 | 0.0000 | 0.0000 |

### Moderate Scarcity Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.90 | 1 | 4.1369 | 0.2069 | 0.5177 |
| `rule` | 1.00 | 0 | 2.8212 | 0.1111 | 0.5867 |
| `llm_survival` | 0.70 | 3 | 4.4193 | 0.3991 | 0.4775 |
| `llm_social_welfare` | 1.00 | 0 | 1.3638 | 0.0458 | 1.0000 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.5622 | 0.0000 | 0.0000 |

### Scarcity Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.20 | 8 | 8.5440 | 0.8251 | 0.5000 |
| `rule` | 1.00 | 0 | 3.1271 | 0.0886 | 0.7633 |
| `llm_survival` | 1.00 | 0 | 4.6018 | 0.1152 | 0.7033 |
| `llm_social_welfare` | 1.00 | 0 | 2.0410 | 0.0762 | 1.0000 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.6145 | 0.0000 | 0.0000 |

---

## Key Observations

### 1. Social-welfare prompting preserved the society

`llm_social_welfare` consistently selected `gather`, which increased food production, lowered food prices, and kept all agents alive in every scenario.

This behavior produced the most stable society-level outcome in this small experiment.

### 2. Wealth-maximizing prompting caused collapse

`llm_wealth_maximizing` over-prioritized `work`, which produced coin but not enough food.

As a result, food scarcity intensified, price reached the maximum level, and all agents died in every scenario.

This shows that individual wealth-focused objectives can produce harmful society-level outcomes when food production is neglected.

### 3. Rule-based policy remained a strong baseline

The `rule` policy kept all agents alive in every scenario.

It did not reduce food price as aggressively as `llm_social_welfare`, but it produced stable and balanced results.

This makes rule-based behavior an important non-LLM baseline.

### 4. Random policy failed under stronger scarcity

The `random` policy survived in the default scenario but collapsed under stronger scarcity.

In the scarcity scenario, only 2 out of 10 agents survived.

This confirms that random behavior is not robust under resource stress.

### 5. Survival prompting was mixed

`llm_survival` did not behave as aggressively as `llm_social_welfare`.

It survived in the default and scarcity scenarios but lost 3 agents in moderate scarcity.

This suggests that the survival objective may require stronger prompt guidance or few-shot examples.

---

## Runtime Note

The zero-shot LLM experiment was noticeably slow on local hardware.

This is expected because each alive agent requests an LLM decision at each timestep.

For this run:

```text
3 LLM policies × 3 scenarios × 10 agents × 30 timesteps
= up to 2700 LLM calls
```

This confirms that future UI and React demos should not run full LLM experiments live.

Instead, the UI should display precomputed logs, summaries, and figures. A small smoke-test mode can be used for live demonstration if needed.

---

## Interpretation

This small experiment supports the main project idea:

> The same local LLM can produce different society-level outcomes when guided by different decision objectives.

The model was kept fixed as `qwen3:8b`. The only difference was the policy objective in the prompt.

The resulting societies behaved very differently:

- Social-welfare objective protected the population.
- Wealth-maximizing objective caused total collapse.
- Survival objective produced mixed results.
- Rule-based behavior remained a strong deterministic baseline.
- Random behavior failed under scarcity.

---

## Limitations

This is still a small-scale experiment.

The results should not be treated as final evidence because:

- only 1 seed was used
- only 10 agents were simulated
- only 30 timesteps were executed
- no few-shot or fine-tuned policy was tested yet

The results are useful as a controlled preliminary comparison before running larger or more targeted experiments.

---

## Next Steps

1. Add few-shot LLM policy.
2. Run `smoke_few_shot.py`.
3. Run a small few-shot comparison under the same conditions.
4. Compare zero-shot vs few-shot behavior.
5. Later, optionally add fine-tuned LLM policy.
# Few-Shot LLM Small Experiment Results

This document records the small controlled comparison between baseline policies, zero-shot LLM policies, and few-shot LLM policies.

This is not the final full-scale experiment. The purpose of this run is to compare early behavior patterns under equal conditions and evaluate whether few-shot prompting reduces the extreme behavior observed in zero-shot LLM policies.

---

## Experiment Setup

| Setting | Value |
|---|---|
| Model | `qwen3:8b` via Ollama |
| Agents | 10 |
| Timesteps | 30 |
| Seed | 1 |
| Scenarios | `default`, `moderate_scarcity`, `scarcity` |
| Baseline policies | `random`, `rule` |
| Zero-shot LLM policies | `llm_survival`, `llm_social_welfare`, `llm_wealth_maximizing` |
| Few-shot LLM policies | `llm_survival_few_shot`, `llm_social_welfare_few_shot`, `llm_wealth_maximizing_few_shot` |

All policies were executed under the same scenario, seed, population size, and timestep settings.

The step logs for this run were saved as a clean snapshot under:

```text
logs_to_read/few_shot_small_experiment/
```

The summary and graphs were generated from that snapshot using:

```bash
python analysis/summarize_experiments.py --log-dir logs_to_read/few_shot_small_experiment
python analysis/plot_results.py --log-dir logs_to_read/few_shot_small_experiment --split-by-scenario
```

---

## Policies Compared

| Policy | Type | Description |
|---|---|---|
| `random` | Baseline | Chooses `gather` or `work` randomly. |
| `rule` | Baseline | Uses hand-written scarcity-aware decision rules. |
| `llm_survival` | Zero-shot LLM | Optimizes individual long-term survival. |
| `llm_social_welfare` | Zero-shot LLM | Optimizes society-level stability, scarcity reduction, and lower inequality. |
| `llm_wealth_maximizing` | Zero-shot LLM | Optimizes individual wealth and coin accumulation. |
| `llm_survival_few_shot` | Few-shot LLM | Uses survival examples to guide the same survival objective. |
| `llm_social_welfare_few_shot` | Few-shot LLM | Uses social-welfare examples to guide the same social-welfare objective. |
| `llm_wealth_maximizing_few_shot` | Few-shot LLM | Uses wealth-maximizing examples with a survival guardrail. |

---

## Summary Results

### Default Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 1.00 | 0 | 1.9809 | 0.0789 | 0.5167 |
| `rule` | 1.00 | 0 | 1.9148 | 0.0645 | 0.4967 |
| `llm_survival` | 1.00 | 0 | 3.6463 | 0.0601 | 0.3933 |
| `llm_survival_few_shot` | 1.00 | 0 | 3.0408 | 0.0649 | 0.4067 |
| `llm_social_welfare` | 1.00 | 0 | 0.9386 | 0.0262 | 1.0000 |
| `llm_social_welfare_few_shot` | 1.00 | 0 | 1.8448 | 0.0540 | 0.4767 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.5108 | 0.0000 | 0.0000 |
| `llm_wealth_maximizing_few_shot` | 1.00 | 0 | 5.9804 | 0.0412 | 0.3400 |

### Moderate Scarcity Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.90 | 1 | 4.1369 | 0.2069 | 0.5177 |
| `rule` | 1.00 | 0 | 2.8212 | 0.1111 | 0.5867 |
| `llm_survival` | 0.70 | 3 | 4.4193 | 0.3991 | 0.4775 |
| `llm_survival_few_shot` | 1.00 | 0 | 3.3404 | 0.0625 | 0.5600 |
| `llm_social_welfare` | 1.00 | 0 | 1.3638 | 0.0458 | 1.0000 |
| `llm_social_welfare_few_shot` | 1.00 | 0 | 2.0052 | 0.0809 | 0.6900 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.5622 | 0.0000 | 0.0000 |
| `llm_wealth_maximizing_few_shot` | 1.00 | 0 | 7.7336 | 0.0624 | 0.4733 |

### Scarcity Scenario

| Policy | Survival | Total Dead | Average Price | Final Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.20 | 8 | 8.5440 | 0.8251 | 0.5000 |
| `rule` | 1.00 | 0 | 3.1271 | 0.0886 | 0.7633 |
| `llm_survival` | 1.00 | 0 | 4.6018 | 0.1152 | 0.7033 |
| `llm_survival_few_shot` | 1.00 | 0 | 3.6360 | 0.0907 | 0.7367 |
| `llm_social_welfare` | 1.00 | 0 | 2.0410 | 0.0762 | 1.0000 |
| `llm_social_welfare_few_shot` | 1.00 | 0 | 2.2627 | 0.0970 | 0.9033 |
| `llm_wealth_maximizing` | 0.00 | 10 | 9.6145 | 0.0000 | 0.0000 |
| `llm_wealth_maximizing_few_shot` | 1.00 | 0 | 9.3497 | 0.0647 | 0.5967 |

---

## Key Findings

### 1. Few-shot prompting fixed the zero-shot wealth collapse

The clearest result is the difference between `llm_wealth_maximizing` and `llm_wealth_maximizing_few_shot`.

| Scenario | Zero-shot Wealth Survival | Few-shot Wealth Survival |
|---|---:|---:|
| `default` | 0.00 | 1.00 |
| `moderate_scarcity` | 0.00 | 1.00 |
| `scarcity` | 0.00 | 1.00 |

The zero-shot wealth-maximizing policy over-prioritized `work`, neglected food production, and collapsed the population in every scenario.

The few-shot wealth-maximizing policy still remained wealth-oriented, but it gathered enough food to keep the population alive. This suggests that few-shot examples added an effective survival guardrail without completely removing the policy's wealth-oriented behavior.

---

### 2. Few-shot survival improved stability under moderate scarcity

The zero-shot survival policy failed under `moderate_scarcity`, while the few-shot survival policy preserved all agents.

| Policy | Survival | Total Dead | Average Price | Final Gini |
|---|---:|---:|---:|---:|
| `llm_survival` | 0.70 | 3 | 4.4193 | 0.3991 |
| `llm_survival_few_shot` | 1.00 | 0 | 3.3404 | 0.0625 |

This indicates that few-shot prompting made the survival objective more stable and less prone to under-producing food during moderate scarcity.

---

### 3. Few-shot social welfare became less blindly gather-focused

The zero-shot social-welfare policy selected `gather` in every scenario with a gather ratio of `1.0000`.

The few-shot social-welfare policy still gathered more as scarcity increased, but it allowed more `work` in safer conditions:

| Scenario | Zero-shot Social Welfare Gather Ratio | Few-shot Social Welfare Gather Ratio |
|---|---:|---:|
| `default` | 1.0000 | 0.4767 |
| `moderate_scarcity` | 1.0000 | 0.6900 |
| `scarcity` | 1.0000 | 0.9033 |

This is a useful behavior pattern. The few-shot social-welfare policy did not abandon the social objective, but it became more context-sensitive.

---

### 4. Rule-based policy remained a strong baseline

The `rule` policy kept all agents alive in every scenario and maintained relatively stable food prices.

This is important because the LLM policies are not being compared only against random behavior. The rule-based policy is a strong deterministic baseline.

---

### 5. Random policy failed under scarcity

The `random` policy performed acceptably in the default scenario but failed under stronger scarcity.

In the `scarcity` scenario, only 2 out of 10 agents survived, and the final population Gini reached `0.8251`.

This confirms that random behavior is not robust under resource stress.

---

## Interpretation

This small experiment supports the main project idea:

> The same local LLM can produce very different society-level outcomes depending on its decision objective and prompting strategy.

The zero-shot policies showed strong objective-driven differences, but they were sometimes too extreme.

Few-shot prompting reduced these extremes:

- Wealth-maximizing behavior no longer caused total collapse.
- Survival prompting became more stable under moderate scarcity.
- Social-welfare prompting became less blindly gather-focused.

At the same time, the few-shot policies did not all become identical. The objectives remained behaviorally distinct:

- Few-shot social welfare remained gather-heavy under scarcity.
- Few-shot wealth maximizing still had higher food prices than social welfare or rule-based behavior.
- Few-shot survival remained between rule-based stability and wealth-oriented risk.

---

## Runtime Note

The few-shot small experiment was slower than the zero-shot experiment because each prompt includes objective-specific examples.

For this run, the LLM-backed calls were approximately:

```text
zero-shot: 3 policies × 3 scenarios × 10 agents × 30 timesteps = up to 2700 LLM calls
few-shot: 3 policies × 3 scenarios × 10 agents × 30 timesteps = up to 2700 LLM calls
```

Few-shot calls are slower because the prompt contains more tokens.

For presentation or UI demos, the full LLM experiment should not be run live. Instead, the UI should display precomputed summaries and graphs. A small smoke-test mode can be used only to demonstrate that the LLM connection works.

---

## Limitations

This is still a small experiment.

The results should not be treated as final evidence because:

- only 1 seed was used
- only 10 agents were simulated
- only 30 timesteps were executed
- the experiment used a single local model: `qwen3:8b`
- no fine-tuned policy was tested yet

The results are useful as a controlled preliminary comparison before larger or more targeted experiments.

---

## Next Steps

1. Improve graph readability further by polishing legend names.
2. Add a `--scenarios` option to `main.py` if selective scenario runs are needed.
3. Decide whether to run a larger final comparison or keep the project focused on small controlled experiments.
4. Add React/UI dashboard using precomputed summaries and figures.
5. Optionally add a fine-tuned LLM policy if time allows.
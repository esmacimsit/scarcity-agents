# AI Society — Project Summary

## 1. Project Overview

AI Society is a small economy-simulation project designed to compare different decision-making policies in a scarcity-based multi-agent environment.

The project started with simple baseline policies and gradually evolved into an LLM-driven policy comparison pipeline:

```text
random / rule-based policies
→ zero-shot LLM policies
→ few-shot LLM policies
→ fine-tuned Qwen3-8B LoRA policy adapters
```

The final phase focuses on integrating fine-tuned LLM policies into the existing simulation and verifying that they produce distinguishable regime-specific behavior.

The three behavior regimes are:

```text
survival
social_welfare
wealth_maximizing
```

Each regime represents a different policy objective:

| Regime | Main Objective | Expected Behavior |
|---|---|---|
| `survival` | Prioritize personal survival | Gather conservatively when food or scarcity risk is high |
| `social_welfare` | Reduce society-level scarcity and instability | Gather more under collective scarcity pressure |
| `wealth_maximizing` | Maximize coin/wealth when safe | Prefer work unless personal survival is threatened |

---

## 2. Simulation Design

The simulation models agents living in a scarcity-based economy. At each timestep, agents choose one of two actions:

```text
gather
work
```

The action affects the agent and the broader environment.

The simulation tracks metrics such as:

```text
alive_count
dead_total
food_price
gather_count
work_count
gini_survivors
gini_population
```

The project uses multiple scenarios to test behavior under different levels of scarcity:

```text
default
moderate_scarcity
scarcity
```

These scenarios allow the same policy to be observed under increasingly difficult economic conditions.

---

## 3. Policy Progression

The project compares policies in stages.

### 3.1 Baseline Policies

The first stage used simple non-LLM baselines:

```text
random
rule
```

The purpose of these policies was to establish basic reference behavior.

- `random` provides a weak baseline with no reasoning.
- `rule` provides a deterministic heuristic baseline.

These policies are useful because they show whether LLM policies provide behavior beyond trivial or manually coded choices.

---

### 3.2 Zero-Shot LLM Policies

The second stage introduced zero-shot LLM policies.

Zero-shot policies use a regime-specific prompt, but no examples.

The zero-shot policies were:

```text
llm_survival
llm_social_welfare
llm_wealth_maximizing
```

The purpose of this phase was to test whether an LLM could follow high-level policy instructions directly from prompts.

Zero-shot behavior is useful, but it can be unstable because the model has to infer the decision boundary only from instructions.

---

### 3.3 Few-Shot LLM Policies

The third stage introduced few-shot prompting.

Few-shot policies added examples to guide the model toward the intended gather/work behavior.

The few-shot policies were:

```text
llm_survival_few_shot
llm_social_welfare_few_shot
llm_wealth_maximizing_few_shot
```

Few-shot prompting made the behavior more controllable than zero-shot prompting because the model saw example decisions before being asked to choose an action.

However, few-shot prompting still depends on runtime LLM generation and prompt quality. It does not permanently change the model behavior.

---

## 4. Fine-Tuned LLM Policy Phase

The final technical phase trained regime-specific LoRA adapters using Qwen3-8B as the base model.

The fine-tuned phase was designed to answer this question:

> Can behavior-specific LoRA adapters be trained and integrated into the simulation as runtime policies?

The answer is yes.

The final selected fine-tuned adapters are:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

The selected runtime policy names are:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

These policies were integrated into the same policy router used by the earlier baseline, zero-shot, and few-shot policies.

---

## 5. Fine-Tuning Dataset Pipeline

The fine-tuning dataset was built from teacher-guided accepted examples.

The validated dataset contained:

```text
1500 total examples
500 survival examples
500 social_welfare examples
500 wealth_maximizing examples
```

The strict dataset validation passed before training.

The dataset was converted into LoRA train/validation JSONL format using:

```text
scripts/convert_finetune_dataset.py
```

The LoRA-ready datasets were written under:

```text
data/lora/
```

For augmented v2 datasets, separate outputs were written under:

```text
data/lora_v2/
```

This separation keeps original v1 datasets and augmented v2 datasets cleanly isolated.

---

## 6. LoRA Smoke Training

Before training the main Qwen3-8B adapters, a small smoke training run was performed with Qwen3-0.6B.

The purpose was infrastructure validation, not final policy quality.

The smoke run verified:

```text
MLX-LM model loading
LoRA training loop
train/validation dataset loading
adapter saving
adapter loading during inference
```

The smoke adapter produced outputs, but it was not treated as a quality checkpoint.

This step was useful because it reduced risk before running larger Qwen3-8B training jobs.

---

## 7. Adapter Selection Process

Each fine-tuned adapter was evaluated with lightweight validation probes.

The probes sampled validation examples and compared:

```text
expected action: gather/work
predicted action: gather/work
```

These probes were not full simulation benchmarks. They were used for adapter debugging and checkpoint selection.

---

## 8. Survival Adapter Result

### 8.1 Survival v1

The first survival adapter was trained on the original survival dataset:

```text
data/lora/survival
```

Adapter path:

```text
adapters/qwen3_8b_survival
```

Validation probe result:

```text
accuracy:      85%
gather recall: 70%
work recall:   100%
```

The main error pattern was:

```text
expected gather → predicted work
```

This showed a mild work bias in risky survival states.

---

### 8.2 Survival Augmentation

The survival dataset was augmented because v1 missed gather-risk states.

The failure pattern was:

```text
medium food
+ high food price
+ high scarcity
+ high deaths
=&gt; expected gather
```

A failure-driven augmented dataset was created:

```text
500 original examples
+ 250 synthetic gather-risk examples
+ 100 synthetic safe-work examples
= 850 combined survival examples
```

The augmentation was documented in:

```text
analysis/survival_augmentation_report.md
```

---

### 8.3 Survival v2

The survival v2 adapter was trained on the augmented dataset.

Adapter path:

```text
adapters/qwen3_8b_survival_v2
```

Original validation probe result:

```text
accuracy:      90%
gather recall: 80%
work recall:   100%
```

The augmented stress validation split remained harder, but v2 did not perform worse than v1 there.

Final decision:

```text
selected survival adapter: adapters/qwen3_8b_survival_v2
```

Reason:

```text
survival v2 improved original validation accuracy
survival v2 improved gather recall
survival v2 preserved work recall
```

---

## 9. Social Welfare Adapter Result

The social welfare adapter was trained on the original social welfare dataset:

```text
data/lora/social_welfare
```

Adapter path:

```text
adapters/qwen3_8b_social_welfare
```

Validation probe result:

```text
accuracy:      95%
gather recall: 100%
work recall:   90%
```

The result was strong enough to accept v1 directly.

No augmentation was needed.

Final decision:

```text
selected social welfare adapter: adapters/qwen3_8b_social_welfare
```

Reason:

```text
strong validation accuracy
perfect gather recall
only one work → gather error
behavior fits the social welfare regime
```

The social welfare policy was the cleanest fine-tuned regime in the adapter-selection phase.

---

## 10. Wealth-Maximizing Adapter Result

### 10.1 Wealth v1

The first wealth-maximizing adapter was trained on the original wealth dataset:

```text
data/lora/wealth_maximizing
```

Adapter path:

```text
adapters/qwen3_8b_wealth_maximizing
```

Validation probe result:

```text
accuracy:      88.89%
gather recall: 75%
work recall:   100%
```

The main error pattern was again:

```text
expected gather → predicted work
```

This was less severe than survival because the wealth regime is intentionally work-heavy. However, wealth-maximizing behavior should still obey the rule:

```text
selfish but not suicidal
```

Therefore, risky personal-survival states still need to produce `gather`.

---

### 10.2 Wealth Augmentation

A smaller targeted augmentation was created for the wealth dataset.

The goal was to improve gather recall without destroying the work-heavy character of the regime.

The augmented wealth dataset was:

```text
500 original examples
+ 100 synthetic gather-risk examples
+ 50 synthetic safe-work examples
= 650 combined wealth examples
```

The augmentation was documented in:

```text
analysis/wealth_augmentation_report.md
```

---

### 10.3 Wealth v2

The wealth v2 adapter was trained on the augmented wealth dataset.

Adapter path:

```text
adapters/qwen3_8b_wealth_maximizing_v2
```

On the augmented stress validation split:

```text
wealth v1 accuracy: 80%
wealth v2 accuracy: 90%
```

Gather recall improved from:

```text
60% → 80%
```

Work recall stayed at:

```text
100%
```

Final decision:

```text
selected wealth adapter: adapters/qwen3_8b_wealth_maximizing_v2
```

Reason:

```text
wealth v2 improved stress validation accuracy
wealth v2 improved gather recall
wealth v2 preserved work recall
wealth v2 better captures selfish-but-not-suicidal behavior
```

---

## 11. Runtime Integration

The selected fine-tuned adapters were integrated into the simulation runtime.

New runtime components:

```text
policies/prompt_builders.py
policies/finetuned.py
```

The policy router was updated in:

```text
policies/__init__.py
```

The router now supports:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

The fine-tuned policy wrapper handles:

```text
regime-to-adapter mapping
prompt building
MLX-LM generation
gather/work output normalization
```

Runtime smoke testing confirmed:

```text
prompt builder import: PASS
fine-tuned policy import: PASS
selected adapter mapping: PASS
MLX-LM generation: PASS
output normalization: PASS
policy router dispatch: PASS
main.py execution: PASS
```

---

## 12. Fine-Tuned Small Experiment

A small controlled experiment was run for the selected fine-tuned policies.

Command:

```bash
PYTHONPATH=. python main.py \
  --policies finetuned_survival finetuned_social_welfare finetuned_wealth_maximizing \
  --seeds 1 \
  --n-agents 2 \
  --timesteps 3
```

Experiment setup:

```text
seed: 1
agents: 2
timesteps: 3
scenarios: default, moderate_scarcity, scarcity
policies: finetuned_survival, finetuned_social_welfare, finetuned_wealth_maximizing
```

The clean step logs were saved under:

```text
logs_to_read/finetuned_small_experiment/
```

The generated summary was saved as:

```text
analysis/finetuned_small_experiment_summary.csv
```

The generated figures were saved under:

```text
analysis/figures/finetuned_small_experiment/
```

---

## 13. Fine-Tuned Small Experiment Results

### 13.1 Default Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 1.7125 | 2 | 0 | 0.0334 |
| `finetuned_social_welfare` | 1.00 | 0 | 2.7397 | 0 | 2 | 0.0356 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 7.4744 | 0 | 2 | 0.0172 |

### 13.2 Moderate Scarcity Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 2.3926 | 2 | 0 | 0.0320 |
| `finetuned_social_welfare` | 1.00 | 0 | 8.2279 | 2 | 0 | 0.0360 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 8.2279 | 0 | 2 | 0.0127 |

### 13.3 Scarcity Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 3.1397 | 2 | 0 | 0.0298 |
| `finetuned_social_welfare` | 1.00 | 0 | 4.6329 | 2 | 0 | 0.0347 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 8.9931 | 0 | 2 | 0.0094 |

---

## 14. Main Findings

### 14.1 Fine-tuned policies ran end-to-end

All selected fine-tuned policies executed through `main.py` without hard runtime failures.

This confirms that the adapter-selection, runtime wrapper, and policy-router integration were successful.

---

### 14.2 Fine-tuned policies showed regime separation

The policies did not collapse into identical behavior.

Observed pattern:

```text
finetuned_survival:          gather-oriented / conservative
finetuned_social_welfare:    shifts toward gather under scarcity pressure
finetuned_wealth_maximizing: work-oriented
```

This is the most important result of the fine-tuned phase.

---

### 14.3 Survival stayed conservative

The survival policy selected `gather` in all tested scenarios.

This matches its purpose: avoid personal risk and protect long-term survival.

---

### 14.4 Social welfare was scenario-sensitive

The social welfare policy selected `work` in the default scenario but shifted toward `gather` under scarcity.

This is a useful sign because the social welfare regime is expected to respond to collective scarcity pressure.

---

### 14.5 Wealth maximizing stayed work-oriented

The wealth policy selected `work` in all tested scenarios.

This matches the intended regime tendency: maximize wealth when personal survival is not immediately critical.

---

### 14.6 Price and gather-ratio figures support the behavior split

The most useful figures are:

```text
analysis/figures/finetuned_small_experiment/gather_ratio_over_time_scarcity.png
analysis/figures/finetuned_small_experiment/price_over_time_scarcity.png
```

The gather-ratio plots show policy separation most clearly.

The price plots support the action pattern:

```text
gather-heavy behavior reduces price pressure
work-heavy behavior allows price pressure to rise
```

Alive-agent plots show no mortality differences because all agents survived in the small run.

Gini plots remain low because the experiment contains only two agents.

---

## 15. Limitations

The final fine-tuned experiment is intentionally small.

Limitations:

```text
one seed
small population size
short horizon
no deaths occurred
no confidence intervals
small-scale behavioral comparison rather than full statistical benchmark
```

These limitations are acceptable for the current phase because the main goal was to show:

```text
fine-tuned adapters can be trained
fine-tuned adapters can be selected
fine-tuned adapters can be integrated into the simulation
fine-tuned policies produce distinguishable behavior
```

---

## 16. Final Project Conclusion

The project successfully built a staged policy-comparison pipeline for an AI society simulation.

The final system includes:

```text
baseline policies
zero-shot LLM policies
few-shot LLM policies
fine-tuned Qwen3-8B LoRA policies
```

The fine-tuned phase successfully produced three selected runtime policies:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

The final small experiment confirmed that the fine-tuned policies can run through the simulation and produce distinct regime-specific behavior.

The main achievement is not only training adapters, but connecting the full pipeline:

```text
dataset creation
validation
augmentation
LoRA training
adapter selection
runtime integration
simulation execution
summary generation
graph reporting
```

This completes the current project phase.
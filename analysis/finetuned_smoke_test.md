# Fine-Tuned Policy Smoke Test Report

## 1. Purpose

This document reports the first simulation-level smoke test for the selected fine-tuned Qwen3-8B LoRA policy adapters.

The goal of this smoke test is not to measure final policy quality. The goal is to verify that the selected fine-tuned policies can run end-to-end inside the existing simulation flow.

The smoke test checks that:

```text
main.py accepts fine-tuned policy names
World calls decide_policy_action
policy router dispatches to policies.finetuned
selected LoRA adapter paths are loaded
MLX-LM generation runs without crashing
model output is normalized to gather/work
simulation logs are produced
```

---

## 2. Selected Fine-Tuned Adapter Set

The selected adapter set used by the runtime policy wrapper is:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

These selections are documented in:

```text
analysis/finetuned_adapter_selection.md
```

---

## 3. Runtime Integration Components

The following runtime components were added:

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

---

## 4. Direct Runtime Wrapper Smoke Test

Before running `main.py`, the fine-tuned runtime wrapper was tested directly with simulation-like states.

The direct runtime test verified:

```text
prompt builder import: PASS
fine-tuned policy import: PASS
selected adapter mapping: PASS
MLX-LM generation: PASS
output normalization: PASS
```

A critical personal-survival-risk state produced `gather` for all three regimes:

```text
finetuned_survival          => gather
finetuned_social_welfare    => gather
finetuned_wealth_maximizing => gather
```

This confirms that the runtime wrapper can call the selected adapters and return valid simulation actions.

---

## 5. Policy Router Smoke Test

The policy router was tested through:

```text
from policies import decide_policy_action
```

The router recognized all fine-tuned policy names:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

A critical personal-survival-risk context produced:

```text
finetuned_survival => gather
finetuned_social_welfare => gather
finetuned_wealth_maximizing => gather
```

Result:

```text
policy router smoke: PASS
```

---

## 6. Simulation-Level Smoke Test

The selected fine-tuned policies were then executed through `main.py`.

Example command pattern:

```bash
PYTHONPATH=. python main.py \
  --policies finetuned_survival \
  --seeds 1 \
  --n-agents 1 \
  --timesteps 2
```

The same smoke pattern was run for:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

The purpose was to verify end-to-end integration, not statistical performance.

---

## 7. Simulation Smoke Results

### 7.1 Fine-Tuned Survival

Observed small-run behavior:

```text
default:           gather=1 work=0
moderate_scarcity: gather=1 work=0
scarcity:          gather=1 work=0
```

Interpretation:

```text
runtime status: PASS
behavior note: survival policy is conservative and gather-oriented in the tiny smoke run
```

### 7.2 Fine-Tuned Social Welfare

Observed small-run behavior:

```text
default:           gather=1 work=0
moderate_scarcity: gather=1 work=0
scarcity:          gather=0 work=1
```

Interpretation:

```text
runtime status: PASS
behavior note: one tiny-run scenario produced work, but this is not a quality failure because the smoke run contains too few decisions for statistical interpretation
```

### 7.3 Fine-Tuned Wealth Maximizing

Observed small-run behavior:

```text
default:           gather=0 work=1
moderate_scarcity: gather=0 work=1
scarcity:          gather=0 work=1
```

Interpretation:

```text
runtime status: PASS
behavior note: wealth policy behaves work-heavy, which matches the intended regime tendency
```

---

## 8. Smoke Test Verdict

The simulation-level fine-tuned policy smoke test passed.

```text
main.py accepted fine-tuned policy names: PASS
policy router dispatch: PASS
adapter loading: PASS
MLX-LM generation: PASS
action normalization: PASS
simulation logs produced: PASS
hard runtime failures: 0
```

Final smoke status:

```text
PASS
```

---

## 9. Important Limitation

This smoke test is intentionally tiny:

```text
n-agents=1
timesteps=2
seed=1
```

Therefore, the action counts should not be interpreted as final policy performance.

The smoke test only proves that the fine-tuned policies can run inside the simulation without crashing.

---

## 10. Next Step: Small Fine-Tuned Comparison Experiment

A small comparison experiment should still be run and reported.

Recommended next experiment:

```bash
PYTHONPATH=. python main.py \
  --policies finetuned_survival finetuned_social_welfare finetuned_wealth_maximizing \
  --seeds 1 \
  --n-agents 2 \
  --timesteps 3
```

This experiment is still small enough to run locally, but it gives more useful comparative signals than the one-agent smoke test.

The small experiment should report:

```text
scenario
policy
seed
alive_count
dead_total
final_price
gather_count
work_count
survival rate
```

The small experiment result should be documented in a separate section or a separate report after execution.

---

## 11. Current Status

Current fine-tuned integration status:

```text
adapter selection: complete
runtime wrapper: complete
policy router integration: complete
simulation-level smoke test: complete
small comparison experiment: pending
```
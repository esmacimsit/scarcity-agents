# Fine-Tuned LLM Small Experiment Results

This document records the small controlled experiment for the selected fine-tuned Qwen3-8B LoRA policy adapters.

This is not a full-scale statistical benchmark. The purpose of this run is to verify that the selected fine-tuned policies can run through the simulation end-to-end and to observe whether their behavior remains distinguishable across scenarios.

---

## Experiment Setup

| Setting | Value |
|---|---|
| Base model | `Qwen/Qwen3-8B` via MLX-LM |
| Fine-tuning method | LoRA adapters |
| Agents | 2 |
| Timesteps | 3 |
| Seed | 1 |
| Scenarios | `default`, `moderate_scarcity`, `scarcity` |
| Fine-tuned policies | `finetuned_survival`, `finetuned_social_welfare`, `finetuned_wealth_maximizing` |

All fine-tuned policies were executed under the same scenario, seed, population size, and timestep settings.

The step logs for this run were saved as a clean snapshot under:

```text
logs_to_read/finetuned_small_experiment/
```

The summary and graphs were generated from that snapshot using:

```bash
PYTHONPATH=. python analysis/summarize_experiments.py \
  --log-dir logs_to_read/finetuned_small_experiment \
  --output analysis/finetuned_small_experiment_summary.csv

PYTHONPATH=. python analysis/plot_results.py \
  --log-dir logs_to_read/finetuned_small_experiment \
  --output-dir analysis/figures/finetuned_small_experiment \
  --split-by-scenario
```

---

## Policies Compared

| Policy | Type | Selected Adapter | Description |
|---|---|---|---|
| `finetuned_survival` | Fine-tuned LoRA | `adapters/qwen3_8b_survival_v2` | Prioritizes personal survival and tends to gather conservatively under risk. |
| `finetuned_social_welfare` | Fine-tuned LoRA | `adapters/qwen3_8b_social_welfare` | Prioritizes society-level stability and responds to scarcity pressure. |
| `finetuned_wealth_maximizing` | Fine-tuned LoRA | `adapters/qwen3_8b_wealth_maximizing_v2` | Prioritizes work and wealth when personal survival is not critically threatened. |

The adapter selection process is documented separately in:

```text
analysis/finetuned_adapter_selection.md
```

---

## Experiment Command

```bash
PYTHONPATH=. python main.py \
  --policies finetuned_survival finetuned_social_welfare finetuned_wealth_maximizing \
  --seeds 1 \
  --n-agents 2 \
  --timesteps 3
```

---

## Summary Results

### Default Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 1.7125 | 2 | 0 | 0.0334 |
| `finetuned_social_welfare` | 1.00 | 0 | 2.7397 | 0 | 2 | 0.0356 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 7.4744 | 0 | 2 | 0.0172 |

### Moderate Scarcity Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 2.3926 | 2 | 0 | 0.0320 |
| `finetuned_social_welfare` | 1.00 | 0 | 8.2279 | 2 | 0 | 0.0360 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 8.2279 | 0 | 2 | 0.0127 |

### Scarcity Scenario

| Policy | Survival | Total Dead | Final Price | Gather | Work | Final Gini |
|---|---:|---:|---:|---:|---:|---:|
| `finetuned_survival` | 1.00 | 0 | 3.1397 | 2 | 0 | 0.0298 |
| `finetuned_social_welfare` | 1.00 | 0 | 4.6329 | 2 | 0 | 0.0347 |
| `finetuned_wealth_maximizing` | 1.00 | 0 | 8.9931 | 0 | 2 | 0.0094 |

---

## Key Findings

### 1. All fine-tuned policies ran successfully inside the simulation

All selected fine-tuned policies executed through `main.py`, produced logs, and completed without hard runtime failures.

```text
hard runtime failures: 0
scenarios completed: default, moderate_scarcity, scarcity
policies completed: finetuned_survival, finetuned_social_welfare, finetuned_wealth_maximizing
```

This confirms that the fine-tuned adapter runtime wrapper and policy router integration work end-to-end.

---

### 2. Fine-tuned policies showed basic regime separation

The policies did not collapse into identical behavior.

Observed pattern:

```text
finetuned_survival:          gather-oriented / conservative
finetuned_social_welfare:    shifts toward gather under scarcity pressure
finetuned_wealth_maximizing: work-oriented
```

This matches the intended high-level policy objectives.

---

### 3. Survival was consistently gather-oriented

The fine-tuned survival policy selected `gather` in every scenario in this small run.

This is consistent with its selected adapter behavior: survival is conservative and prioritizes avoiding personal risk.

---

### 4. Social welfare became more gather-oriented under scarcity

The social-welfare policy selected `work` in the default scenario but shifted to `gather` under `moderate_scarcity` and `scarcity`.

This is the most useful behavior pattern from the small experiment because it shows scenario sensitivity.

---

### 5. Wealth maximizing remained work-oriented

The fine-tuned wealth-maximizing policy selected `work` in all three scenarios in this small experiment.

This matches the intended regime tendency: maximize wealth and coin when survival is not immediately critical.

---

## Figure Outputs

The scenario-split figures were generated under:

```text
analysis/figures/finetuned_small_experiment/
```

Expected figure count:

```text
12 PNG files
3 scenarios × 4 metrics
```

The most useful figures for final reporting are:

```text
analysis/figures/finetuned_small_experiment/gather_ratio_over_time_scarcity.png
analysis/figures/finetuned_small_experiment/price_over_time_scarcity.png
analysis/figures/finetuned_small_experiment/alive_over_time_scarcity.png
analysis/figures/finetuned_small_experiment/gini_population_over_time_scarcity.png
```

Graph interpretation:

- Alive-agent plots show no mortality differences because all agents survived in this small run.
- Gather-ratio plots show the clearest regime separation.
- Price plots support the action-pattern interpretation: gather-heavy behavior reduces price pressure, while work-heavy behavior allows price to rise.
- Gini plots remain low overall because the experiment contains only two agents.

---

## Runtime Note

Fine-tuned policy execution is slower than rule-based policies because each decision calls MLX-LM generation with a selected LoRA adapter.

For this small run, the maximum fine-tuned calls were limited by:

```text
3 policies × 3 scenarios × 2 agents × 3 timesteps = up to 54 fine-tuned decisions
```

This scale was enough to verify integration and produce a compact behavior comparison.

---

## Interpretation

This small experiment supports the current fine-tuned phase goal:

> Selected fine-tuned Qwen3-8B LoRA adapters can be integrated into the simulation and produce distinct regime-specific behavior.

The results are intentionally compact, but they are enough to show:

- adapter selection was successful enough for runtime use
- the policy router can call fine-tuned policies
- all selected adapters execute through the simulation path
- the resulting policies are behaviorally distinguishable

---

## Limitations

This is a small experiment.

The results should not be treated as a final statistical benchmark because:

- only 1 seed was used
- only 2 agents were simulated
- only 3 timesteps were executed
- no deaths occurred
- no confidence intervals were computed

The results are sufficient for the current project scope because the goal of this phase is end-to-end fine-tuned policy integration and basic behavioral verification.

---

## Verdict

The fine-tuned small comparison experiment passed.

```text
adapter selection: complete
runtime integration: complete
policy router integration: complete
simulation smoke test: complete
small comparison experiment: complete
clean logs snapshot: complete
scenario-split figures: complete
```

---

## Next Steps

1. Use the clean logs and figures in the final project findings summary.
2. Compare the fine-tuned behavior against the zero-shot and few-shot findings at a high level.
3. Finalize the project documentation.
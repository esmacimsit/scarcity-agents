# AI Society

AI Society is a small scarcity-based economy simulation for comparing different agent decision policies.

The project starts from simple baseline policies and extends into LLM-based decision policies:

```text
random / rule-based
→ zero-shot LLM
→ few-shot LLM
→ fine-tuned Qwen3-8B LoRA adapters
```

The final project phase integrates selected fine-tuned LoRA adapters into the simulation runtime and verifies that they produce distinct regime-specific behavior.

---

## Policy Regimes

The project compares three high-level behavior regimes:

| Regime | Goal | Expected Behavior |
|---|---|---|
| `survival` | Personal survival | Gather conservatively when risk is high |
| `social_welfare` | Society-level stability | Gather more under collective scarcity |
| `wealth_maximizing` | Personal wealth | Prefer work when survival is safe |

Agents choose one action per timestep:

```text
gather
work
```

---

## Project Structure

```text
ai_society/
├── main.py                         # Main experiment runner
├── world.py                        # Simulation environment
├── agent.py                        # Agent state/action handling
├── policies/                       # Runtime policy implementations
│   ├── random_policy.py
│   ├── rule_based.py
│   ├── zero_shot.py
│   ├── few_shot.py
│   ├── prompt_builders.py
│   └── finetuned.py
├── scripts/                        # Dataset, augmentation, and conversion scripts
├── smoke_tests/                    # Runtime and adapter smoke tests
├── analysis/                       # Reports, summaries, and figures
├── logs/                           # Raw simulation logs
├── logs_to_read/                   # Clean log snapshots used in reports
├── data/                           # Training/evaluation data
└── MILESTONES.MD                   # Project progress tracker
```

---

## Final Selected Fine-Tuned Adapters

The final selected Qwen3-8B LoRA adapters are:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

Runtime policy names:

```text
finetuned_survival
finetuned_social_welfare
finetuned_wealth_maximizing
```

Adapter selection details are documented in:

```text
analysis/finetuned_adapter_selection.md
```

---

## Setup

Create and activate the project environment:

```bash
conda activate ai_society
```

Install dependencies as needed for the local environment. The fine-tuned runtime uses MLX-LM on Apple Silicon:

```bash
python -m mlx_lm --help
```

---

## Running the Simulation

Run a small baseline experiment:

```bash
PYTHONPATH=. python main.py \
  --policies random rule \
  --seeds 1 \
  --n-agents 5 \
  --timesteps 10
```

Run the selected fine-tuned policies:

```bash
PYTHONPATH=. python main.py \
  --policies finetuned_survival finetuned_social_welfare finetuned_wealth_maximizing \
  --seeds 1 \
  --n-agents 2 \
  --timesteps 3
```

Fine-tuned runs are intentionally kept small because each decision calls MLX-LM generation with a selected LoRA adapter.

---

## Generating Summaries and Figures

Generate a CSV summary from a clean log snapshot:

```bash
PYTHONPATH=. python analysis/summarize_experiments.py \
  --log-dir logs_to_read/finetuned_small_experiment \
  --output analysis/finetuned_small_experiment_summary.csv
```

Generate scenario-split figures:

```bash
PYTHONPATH=. python analysis/plot_results.py \
  --log-dir logs_to_read/finetuned_small_experiment \
  --output-dir analysis/figures/finetuned_small_experiment \
  --split-by-scenario
```

The fine-tuned experiment figures are stored under:

```text
analysis/figures/finetuned_small_experiment/
```

The clean fine-tuned log snapshot is stored under:

```text
logs_to_read/finetuned_small_experiment/
```

---

## Main Reports

| File | Purpose |
|---|---|
| `SUMMARY.md` | Final technical project summary and findings |
| `MILESTONES.MD` | Project progress checklist |
| `analysis/finetuned_adapter_selection.md` | Fine-tuned adapter selection and augmentation decisions |
| `analysis/finetuned_smoke_test.md` | Runtime and simulation-level smoke test report |
| `analysis/finetuned_small_experiment_report.md` | Fine-tuned small comparison experiment report |
| `analysis/survival_augmentation_report.md` | Survival failure-driven augmentation report |
| `analysis/wealth_augmentation_report.md` | Wealth failure-driven augmentation report |

---

## Key Final Result

The final fine-tuned phase completed successfully:

```text
adapter selection: complete
runtime integration: complete
policy router integration: complete
simulation smoke test: complete
small fine-tuned comparison experiment: complete
clean logs and figures: complete
```

The final small experiment showed basic regime separation:

```text
finetuned_survival:          gather-oriented / conservative
finetuned_social_welfare:    shifts toward gather under scarcity pressure
finetuned_wealth_maximizing: work-oriented
```

This confirms that the selected fine-tuned Qwen3-8B LoRA adapters can run inside the simulation and produce distinguishable behavior.

---

## Notes

Large model adapters and generated JSONL datasets are intentionally ignored by Git.

Important generated artifacts are documented through reports, clean log snapshots, summaries, and figures rather than committing model weights or large training datasets.

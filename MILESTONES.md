# Project Milestones

This file tracks the development milestones of the AI Society project.

The project studies how different decision policies manipulate society-level economic outcomes in a scarcity-based multi-agent simulation.

---

## CH1 — Baseline Society Simulation

- [x] CH1-001 Build world simulation loop
- [x] CH1-002 Add agent state: food, coin, productivity, wealth
- [x] CH1-003 Add gather/work actions
- [x] CH1-004 Add food price dynamics
- [x] CH1-005 Add death/survival logic
- [x] CH1-006 Add Gini calculation
- [x] CH1-007 Add random policy
- [x] CH1-008 Add rule-based scarcity-aware policy
- [x] CH1-009 Add step_log and agent_log CSV outputs
- [x] CH1-010 Run baseline experiments
- [x] CH1-011 Generate baseline summary and graphs

---

## CH2 — Zero-Shot LLM Policies

- [x] CH2-001 Refactor policy architecture
- [x] CH2-002 Add LLM policy names
- [x] CH2-003 Add zero-shot prompt builder
- [x] CH2-004 Add local LLM client using Ollama/Qwen
- [x] CH2-005 Connect world.py to LLM policy router
- [x] CH2-006 Add zero-shot smoke test
- [x] CH2-007 Add main.py policy-set switch
- [x] CH2-008 Run zero-shot small comparison experiment
- [x] CH2-009 Update summary/plot parser for LLM policy names
- [x] CH2-010 Save clean zero-shot experiment snapshot
- [x] CH2-011 Write zero-shot experiment report

---

## CH3 — Few-Shot LLM Policies

- [x] CH3-001 Decide few-shot policy names and example strategy
- [x] CH3-002 Add few-shot prompt builder
- [x] CH3-003 Add few-shot policy module
- [x] CH3-004 Connect few-shot policies to router
- [x] CH3-005 Add few-shot policy-set to main.py
- [x] CH3-006 Update analysis parsers for few-shot policies
- [x] CH3-007 Add few-shot smoke test
- [x] CH3-008 Run few-shot smoke test and save CSV
- [x] CH3-009 Write few-shot smoke test report
- [x] CH3-010 Run small few-shot comparison experiment
- [x] CH3-011 Save clean few-shot experiment snapshot
- [x] CH3-012 Add --log-dir to summary/plot scripts
- [x] CH3-013 Add --split-by-scenario to plot script
- [x] CH3-014 Write few-shot small experiment report

---

## CH4 — Fine-Tuned LLM Policies

- [x] CH4-001 Decide fine-tune objective strategy
- [x] CH4-002 Decide fine-tune architecture: three separate LoRA adapters, with single adapter as fallback
- [x] CH4-003 Define fine-tune training data schema
- [x] CH4-004 Create finetune_plan.md
- [x] CH4-005 Create data/finetune directory structure
- [x] CH4-006 Add teacher-guided fine-tune dataset generator
- [x] CH4-007 Add hybrid validator rules for survival, social welfare, and wealth maximizing
- [x] CH4-008 Generate first teacher-guided fine-tune decision dataset
- [x] CH4-009 Validate dataset class balance, coverage, duplicates, and gather/work ratios
- [x] CH4-010 Write fine-tune dataset generation path and validation report
- [x] CH4-010A Add cache/resume support for teacher-guided generation
- [x] CH4-010B Add batch-level teacher prompt/response logging
- [x] CH4-010C Add strict validation thresholds and duplicate/conflict checks
- [x] CH4-010D Generate 300-per-regime teacher-guided seed dataset and pass strict validation
- [x] CH4-010E Generate 500-per-regime teacher-guided dataset and pass strict validation
- [x] CH4-011 Decide fine-tuning method and target model: Qwen3 family, Qwen3-8B final target
- [x] CH4-012 Convert decision dataset to LoRA train/validation format
- [x] CH4-013 Run mini Qwen3-0.6B LoRA smoke training
- [x] CH4-013A Run LoRA smoke inference test and document infrastructure result
- [x] CH4-013B Train Qwen3-8B survival adapter
- [x] CH4-013B1 Run survival fine-tuned validation probes
- [x] CH4-013B2 Add failure-driven survival augmentation
- [x] CH4-013B3 Train Qwen3-8B survival v2 adapter
- [x] CH4-013B4 Compare survival v1/v2 adapters and select survival v2
- [x] CH4-013C Train Qwen3-8B social_welfare adapter
- [x] CH4-013D Train Qwen3-8B wealth_maximizing adapter
- [x] CH4-013D1 Add failure-driven wealth_maximizing augmentation
- [x] CH4-013D2 Train Qwen3-8B wealth_maximizing v2 adapter
- [x] CH4-013E Select best checkpoint per behavior regime
- [x] CH4-014 Save fine-tuned model or adapter
- [x] CH4-015 Add fine-tuned prompt builder
- [x] CH4-016 Add fine-tuned policy module
- [x] CH4-017 Connect fine-tuned policies to router
- [x] CH4-018 Add fine-tuned policy-set to main.py
- [x] CH4-019 Update analysis parsers for fine-tuned policies
- [x] CH4-020 Add fine-tuned smoke test
- [x] CH4-021 Run fine-tuned smoke test and save CSV/log outputs
- [x] CH4-022 Write fine-tuned smoke test report
- [x] CH4-023 Run small fine-tuned comparison experiment
- [x] CH4-024 Save clean fine-tuned experiment snapshot
- [x] CH4-025 Generate fine-tuned summary and scenario-split graphs
- [x] CH4-026 Write fine-tuned small experiment report
- [x] CH4-027 Compare zero-shot vs few-shot vs fine-tuned behavior
- [x] CH4-028 Decide final experiment scale
- [x] CH4-029 Run final comparison experiment if needed
- [ ] CH4-030 Write final project findings summary

---

## Current Status

Core comparison workflow is complete through CH3.

Completed policy groups:

- random baseline
- rule-based baseline
- zero-shot LLM policies
- few-shot LLM policies

Current CH4 status:

- fine-tune strategy decided: three separate LoRA adapters, with single adapter as fallback
- final target model strategy documented: Qwen3-8B with Qwen3-0.6B smoke testing
- teacher-guided dataset pipeline implemented
- Hugging Face teacher model integration tested
- cache/resume support implemented and tested
- batch-level teacher logging implemented
- duplicate/conflict validation implemented
- strict validation thresholds implemented
- 500 accepted examples per regime generated
- strict dataset validation passed
- dataset backup zip created outside the tracked JSONL flow
- accepted dataset converted to LoRA train/validation chat JSONL format
- Qwen3-0.6B MLX LoRA smoke training completed
- LoRA inference smoke test completed and documented as an infrastructure check
- Qwen3-8B survival adapter v1 trained and probed
- survival v1 showed mild work bias on validation probes
- failure-driven survival augmentation created v2 dataset
- Qwen3-8B survival adapter v2 trained and selected as current best survival checkpoint
- survival v1/v2 comparison report documented
- Qwen3-8B social_welfare adapter trained, probed, and accepted without augmentation
- Qwen3-8B wealth_maximizing adapter v1 trained and probed
- wealth_maximizing v1 showed mild work bias on gather-risk validation probes
- failure-driven wealth_maximizing augmentation created v2 dataset
- Qwen3-8B wealth_maximizing adapter v2 trained and selected as current best wealth checkpoint
- final fine-tuned adapter selection report documented
- fine-tuned runtime prompt builder implemented
- fine-tuned policy module implemented
- fine-tuned policies connected to policy router
- fine-tuned policies executed through main.py smoke runs without hard runtime failures
- fine-tuned smoke test report documented
- small fine-tuned comparison experiment completed
- fine-tuned small experiment report documented
- fine-tuned experiment produced logs across default, moderate_scarcity, and scarcity scenarios
- fine-tuned policies showed basic regime separation in the small experiment
- analysis parser flow supports fine-tuned policy names through the existing policy/log naming path
- final experiment scale decided: the completed small fine-tuned comparison experiment is sufficient for the current project scope
- no additional fine-tuned comparison experiment is required for this phase

Current dataset checkpoint:

```text
survival:          500 accepted / 1 rejected / 99.8% acceptance
social_welfare:    500 accepted / 9 rejected / 98.2% acceptance
wealth_maximizing: 500 accepted / 1 rejected / 99.8% acceptance

global:            1500 accepted / 11 rejected / 99.3% acceptance
strict status:     PASS
```

Current survival adapter checkpoint:

```text
survival v1 adapter: adapters/qwen3_8b_survival
survival v2 adapter: adapters/qwen3_8b_survival_v2
selected survival adapter: survival v2

v1 original validation probe: 85% accuracy, gather recall 70%, work recall 100%
v2 original validation probe: 90% accuracy, gather recall 80%, work recall 100%
augmented stress validation: v1 and v2 both 70%
```

Current selected fine-tuned adapter set:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

Current adapter probe checkpoint:

```text
survival selected adapter: survival v2
survival original validation probe: 90% accuracy, gather recall 80%, work recall 100%

social_welfare selected adapter: social_welfare v1
social_welfare validation probe: 95% accuracy, gather recall 100%, work recall 90%

wealth_maximizing selected adapter: wealth_maximizing v2
wealth_maximizing stress validation probe: 90% accuracy, gather recall 80%, work recall 100%
```

Fine-tuned runtime integration checkpoint:

```text
prompt builder: complete
policy module: complete
policy router integration: complete
main.py fine-tuned smoke runs: PASS
hard runtime failures: 0
```

Current fine-tuned small experiment checkpoint:

```text
experiment scale: seed=1, agents=2, timesteps=3
policies: finetuned_survival, finetuned_social_welfare, finetuned_wealth_maximizing
scenarios: default, moderate_scarcity, scarcity
status: PASS
hard runtime failures: 0
report: analysis/finetuned_small_experiment_report.md

observed behavior:
- survival: gather-oriented / conservative
- social_welfare: shifts toward gather under scarcity pressure
- wealth_maximizing: work-oriented
```

Final experiment scale decision:

```text
Decision: the completed small fine-tuned comparison experiment is the final experiment for the current project phase.

Rationale:
- adapter selection is complete
- runtime integration is complete
- smoke tests passed
- small experiment ran through all selected fine-tuned policies and scenarios
- logs were produced successfully
- the observed behavior shows basic regime separation

No additional comparison experiment is required for this phase.
```

Next active phase:

- CH4-030 — Write final project findings summary
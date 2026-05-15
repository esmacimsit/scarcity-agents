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

- [ ] CH4-001 Decide fine-tune objective strategy
- [ ] CH4-002 Decide single fine-tuned model vs three separate models
- [ ] CH4-003 Define fine-tune training data schema
- [ ] CH4-004 Create finetune_plan.md
- [ ] CH4-005 Create data/finetune directory structure
- [ ] CH4-006 Add synthetic fine-tune dataset generator
- [ ] CH4-007 Add hybrid labeling rules for survival, social welfare, and wealth maximizing
- [ ] CH4-008 Generate first fine-tune decision dataset
- [ ] CH4-009 Validate dataset class balance and gather/work ratios
- [ ] CH4-010 Write fine-tune dataset report
- [ ] CH4-011 Decide fine-tuning method and target model
- [ ] CH4-012 Convert decision dataset to training format
- [ ] CH4-013 Run mini fine-tune / adapter training
- [ ] CH4-014 Save fine-tuned model or adapter
- [ ] CH4-015 Add fine-tuned prompt builder
- [ ] CH4-016 Add fine-tuned policy module
- [ ] CH4-017 Connect fine-tuned policies to router
- [ ] CH4-018 Add fine-tuned policy-set to main.py
- [ ] CH4-019 Update analysis parsers for fine-tuned policies
- [ ] CH4-020 Add fine-tuned smoke test
- [ ] CH4-021 Run fine-tuned smoke test and save CSV
- [ ] CH4-022 Write fine-tuned smoke test report
- [ ] CH4-023 Run small fine-tuned comparison experiment
- [ ] CH4-024 Save clean fine-tuned experiment snapshot
- [ ] CH4-025 Generate fine-tuned summary and scenario-split graphs
- [ ] CH4-026 Write fine-tuned small experiment report
- [ ] CH4-027 Compare zero-shot vs few-shot vs fine-tuned behavior
- [ ] CH4-028 Decide final experiment scale
- [ ] CH4-029 Run final comparison experiment if needed
- [ ] CH4-030 Write final project findings summary

---

## Current Status

Core comparison workflow is complete through CH3.

Completed policy groups:

- random baseline
- rule-based baseline
- zero-shot LLM policies
- few-shot LLM policies

Next active phase:

- CH4 — Fine-Tuned LLM Policies
# Survival Dataset Augmentation Report

## Purpose

Failure-driven augmentation was applied to the survival dataset after the first Qwen3-8B survival adapter showed a work bias on validation probes.

Observed v1 issue:

```text
work recall:   strong
gather recall: weaker
main error:    gather → work
```

The augmentation focuses on medium-food survival crisis states where the correct action should remain `gather`.

## Input Dataset

```text
input: data/finetune/survival/teacher_guided_accepted.jsonl
original total: 500
original gather: 218
original work: 282
```

## Synthetic Targets

```text
target synthetic gather-risk examples: 250
target synthetic safe-work examples:   100
```

## Generated Dataset

```text
augmented total: 350
augmented gather: 250
augmented work: 100

combined total: 850
combined gather: 468
combined work: 382
```

## Candidate Filtering

```text
rejected candidates: 0
duplicate candidates: 0
```

## Output Files

```text
augmented: data/finetune/survival/survival_augmented_accepted.jsonl
combined:  data/finetune/survival/survival_combined_accepted.jsonl
```

## Notes

The original teacher-guided dataset remains unchanged.

The combined dataset should be converted into a separate LoRA v2 dataset and trained into a separate adapter path, for example:

```text
data/lora_v2/survival
adapters/qwen3_8b_survival_v2
```

# Wealth-Maximizing Dataset Augmentation Report

## Purpose

Failure-driven augmentation was applied to the wealth_maximizing dataset after the first Qwen3-8B wealth adapter showed mild work bias on gather-risk validation probes.

Observed v1 issue:

```text
work recall:   strong
gather recall: weaker
main error:    gather → work
```

The augmentation focuses on personal-survival risk states where even a wealth-maximizing policy should choose `gather`.

## Input Dataset

```text
input: data/finetune/wealth_maximizing/teacher_guided_accepted.jsonl
original total: 500
original gather: 135
original work: 365
```

## Synthetic Targets

```text
target synthetic gather-risk examples: 100
target synthetic safe-work examples:   50
```

## Generated Dataset

```text
augmented total: 150
augmented gather: 100
augmented work: 50

combined total: 650
combined gather: 235
combined work: 415
```

## Candidate Filtering

```text
rejected candidates: 0
duplicate candidates: 0
```

## Output Files

```text
augmented: data/finetune/wealth_maximizing/wealth_augmented_accepted.jsonl
combined:  data/finetune/wealth_maximizing/wealth_combined_accepted.jsonl
```

## Notes

The original teacher-guided dataset remains unchanged.

The combined dataset should be converted into a separate LoRA v2 dataset and trained into a separate adapter path, for example:

```text
data/lora_v2/wealth_maximizing
adapters/qwen3_8b_wealth_maximizing_v2
```

# Fine-Tuned Adapter Selection Report

## 1. Purpose

This document summarizes the current adapter selection process for the three fine-tuned Qwen3-8B policy adapters:

```text
survival
social_welfare
wealth_maximizing
```

The goal is to track:

```text
which adapters were trained
which adapters were augmented
why augmentation was needed
which checkpoint is currently selected
what still needs to be completed
```

This is a lightweight adapter-selection report. It is not the final simulation-level policy evaluation.

---

## 2. Base Model and Adapter Strategy

All regime-specific adapters use the same base model:

```text
Qwen/Qwen3-8B
```

The project trains separate LoRA adapters per behavior regime:

```text
survival adapter
social_welfare adapter
wealth_maximizing adapter
```

This keeps the regime behaviors separated while using the same base model and the same LoRA training pipeline.

---

## 3. Evaluation Method

Adapter behavior was checked using lightweight validation probes from:

```text
smoke_tests/fine_tuned_valid_probe.py
```

Each probe samples validation examples from the relevant LoRA dataset and compares model output against the teacher-guided label:

```text
expected action: gather/work
predicted action: gather/work
```

Typical probe size:

```text
10 gather examples
10 work examples
20 total examples when both classes have enough validation examples
```

For regimes where the validation split contains fewer gather examples, the total can be smaller.

These probes are used for adapter selection and debugging. They are not the final policy evaluation inside the full simulation.

---

## 4. Summary Table

| Regime | V1 Adapter | V2 Adapter | Augmented? | Current Selection | Reason |
|---|---|---|---|---|---|
| `survival` | `adapters/qwen3_8b_survival` | `adapters/qwen3_8b_survival_v2` | Yes | `survival_v2` | V2 improved original validation accuracy and gather recall while preserving work recall |
| `social_welfare` | `adapters/qwen3_8b_social_welfare` | Not created | No | `social_welfare_v1` | V1 achieved strong validation probe performance; no augmentation needed for now |
| `wealth_maximizing` | `adapters/qwen3_8b_wealth_maximizing` | `adapters/qwen3_8b_wealth_maximizing_v2` | Yes | `wealth_maximizing_v2` | V2 improved augmented stress validation accuracy from 80% to 90% while preserving 100% work recall |

---

## 5. Survival Adapter Selection

### 5.1 V1 Training

The first survival adapter was trained on the validated teacher-guided survival dataset:

```text
data/lora/survival
```

Dataset size:

```text
500 total examples
450 train
50 valid
```

Adapter path:

```text
adapters/qwen3_8b_survival
```

### 5.2 V1 Probe Result

V1 on original validation set:

```text
Accuracy: 85.00%
Expected gather: 10
Expected work:   10
Predicted gather: 7
Predicted work:   13
```

Confusion summary:

```text
expected=gather predicted=gather count=7
expected=gather predicted=work   count=3
expected=work   predicted=work   count=10
```

Interpretation:

```text
work recall:   100%
gather recall: 70%
main error:    gather → work
```

The v1 survival adapter showed a mild work bias. It handled work examples well but missed some gather-risk states.

### 5.3 Why Survival Was Augmented

The incorrect gather examples shared a pattern:

```text
medium food
+ high food price
+ high scarcity
+ high deaths
=> expected gather
```

In these states, a survival-focused policy should choose `gather`, but v1 sometimes predicted `work`.

To address this, failure-driven augmentation was applied to strengthen the gather-risk decision boundary.

### 5.4 Survival V2 Dataset

The augmented survival v2 dataset was created as:

```text
500 original teacher-guided examples
+ 250 synthetic gather-risk examples
+ 100 synthetic safe-work examples
= 850 combined survival examples
```

Converted v2 LoRA dataset:

```text
data/lora_v2/survival
```

V2 split:

```text
850 total examples
765 train
85 valid
```

V2 adapter path:

```text
adapters/qwen3_8b_survival_v2
```

### 5.5 V2 Probe Result

V2 on original validation set:

```text
Accuracy: 90.00%
Expected gather: 10
Expected work:   10
Predicted gather: 8
Predicted work:   12
```

Confusion summary:

```text
expected=gather predicted=gather count=8
expected=gather predicted=work   count=2
expected=work   predicted=work   count=10
```

Interpretation:

```text
work recall:   100%
gather recall: 80%
main error:    gather → work, reduced from 3 to 2 cases
```

Compared with v1, v2 improved original validation accuracy from `85%` to `90%` and improved gather recall from `70%` to `80%` while preserving work recall.

### 5.6 Stress Validation Result

V2 on augmented / v2 validation set:

```text
Accuracy: 70.00%
Expected gather: 10
Expected work:   10
```

V1 on augmented / v2 validation set:

```text
Accuracy: 70.00%
Expected work:   10
Expected gather: 10
Predicted gather: 10
Predicted work:   10
```

V1 and V2 both reached `70%` on the augmented validation set. This suggests that the augmented split behaves like a harder boundary-focused stress set rather than showing a clear v2 regression.

### 5.7 Survival Decision

Selected survival adapter:

```text
adapters/qwen3_8b_survival_v2
```

Reason:

```text
V2 improves performance on the original validation probe.
V2 improves gather recall from 70% to 80%.
V2 preserves work recall at 100%.
V2 does not perform worse than V1 on the augmented stress validation set.
```

The v1 adapter should be kept as a baseline:

```text
adapters/qwen3_8b_survival
```

---

## 6. Social Welfare Adapter Selection

### 6.1 V1 Training

The social welfare adapter was trained on the validated teacher-guided social welfare dataset:

```text
data/lora/social_welfare
```

Dataset size:

```text
500 total examples
450 train
50 valid
```

Adapter path:

```text
adapters/qwen3_8b_social_welfare
```

### 6.2 V1 Probe Result

Social welfare v1 validation probe:

```text
Total: 20
Correct: 19
Accuracy: 95.00%
```

Confusion summary:

```text
expected=gather predicted=gather count=10
expected=work   predicted=work   count=9
expected=work   predicted=gather count=1
```

Interpretation:

```text
gather recall: 100%
work recall:   90%
overall:       95%
```

### 6.3 Why Social Welfare Was Not Augmented

The social welfare adapter did not show the same problem pattern as survival.

The result was strong enough to keep v1:

```text
95% lightweight validation accuracy
100% gather recall
90% work recall
only one work → gather error
```

The single work-to-gather error is acceptable for a social welfare policy because this regime is intentionally more gather-heavy and prioritizes collective scarcity reduction.

### 6.4 Social Welfare Decision

Selected social welfare adapter:

```text
adapters/qwen3_8b_social_welfare
```

No v2 augmentation is needed for now.

---

## 7. Wealth-Maximizing Adapter Selection

### 7.1 V1 Training

The wealth-maximizing adapter was trained on the validated teacher-guided wealth dataset:

```text
data/lora/wealth_maximizing
```

Dataset size:

```text
500 total examples
450 train
50 valid
```

Adapter path:

```text
adapters/qwen3_8b_wealth_maximizing
```

### 7.2 V1 Probe Result

Wealth v1 validation probe:

```text
Total: 18
Correct: 16
Accuracy: 88.89%
```

The total was 18 instead of 20 because the wealth validation split did not contain 10 gather examples.

Interpretation:

```text
gather recall: 6/8  = 75%
work recall:   10/10 = 100%
main error:    gather → work
```

### 7.3 Why Wealth Needs Augmentation

The wealth regime is expected to be work-heavy, but it should still obey the principle:

```text
selfish but not suicidal
```

The v1 adapter missed some gather-risk examples where personal survival was at risk.

Example failure pattern:

```text
low-to-medium food
+ low/medium coin
+ high food price
+ high scarcity
=> expected gather
```

A targeted wealth v2 augmentation is therefore justified, but it should be smaller than survival augmentation so the wealth-maximizing behavior remains work-heavy.

### 7.4 Wealth V2 Dataset

The wealth v2 dataset was created as:

```text
500 original teacher-guided examples
+ 100 synthetic gather-risk examples
+ 50 synthetic safe-work examples
= 650 combined wealth examples
```

Converted v2 LoRA dataset:

```text
data/lora_v2/wealth_maximizing
```

V2 adapter path:

```text
adapters/qwen3_8b_wealth_maximizing_v2
```

### 7.5 Wealth V2 Probe Result

Wealth v2 on augmented / v2 validation set:

```text
Accuracy: 90.00%
Expected gather: 10
Expected work:   10
```

Confusion summary:

```text
expected=gather predicted=gather count=8
expected=gather predicted=work   count=2
expected=work   predicted=work   count=10
```

Interpretation:

```text
gather recall: 80%
work recall:   100%
overall:       90%
```

### 7.6 Wealth V1 on Augmented / V2 Validation Set

Wealth v1 was also tested on the same augmented / v2 validation split for a fair comparison.

```text
Accuracy: 80.00%
Expected gather: 10
Expected work:   10
```

Confusion summary:

```text
expected=gather predicted=gather count=6
expected=gather predicted=work   count=4
expected=work   predicted=work   count=10
```

Interpretation:

```text
gather recall: 60%
work recall:   100%
overall:       80%
```

Compared with v1 on the same stress validation split, v2 improved accuracy from `80%` to `90%` and improved gather recall from `60%` to `80%` while preserving `100%` work recall.

### 7.7 Wealth Decision

Selected wealth adapter:

```text
adapters/qwen3_8b_wealth_maximizing_v2
```

Reason:

```text
V2 improves augmented stress validation accuracy from 80% to 90%.
V2 improves gather recall from 60% to 80% on the stress validation split.
V2 preserves work recall at 100%.
V2 better captures the "selfish but not suicidal" gather-risk cases.
```

The v1 adapter should be kept as a baseline:

```text
adapters/qwen3_8b_wealth_maximizing
```

---

## 8. Current Selected Adapters

Current selected adapters:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

Current baselines to keep:

```text
survival v1:          adapters/qwen3_8b_survival
wealth_maximizing v1: adapters/qwen3_8b_wealth_maximizing
```

---

## 9. Final Adapter Set

The selected fine-tuned adapter set is:

```text
survival:          adapters/qwen3_8b_survival_v2
social_welfare:    adapters/qwen3_8b_social_welfare
wealth_maximizing: adapters/qwen3_8b_wealth_maximizing_v2
```

All three adapters are now selected.

---

## 10. Next Steps

After adapter selection, the next engineering steps are:

```text
1. Add fine-tuned prompt builder.
2. Add fine-tuned policy module.
3. Connect selected adapters to the policy router.
4. Run simulation-level fine-tuned smoke test.
5. Run small fine-tuned comparison experiment.
```
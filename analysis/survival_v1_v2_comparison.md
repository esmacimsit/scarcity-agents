# Survival Adapter V1/V2 Comparison

## 1. Purpose

This document compares the first Qwen3-8B survival LoRA adapter against the failure-driven augmented survival v2 adapter.

The goal is to decide which survival adapter should be kept as the current best checkpoint before moving on to the `social_welfare` and `wealth_maximizing` adapters.

---

## 2. Background

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

The first validation probe showed a directional error pattern:

```text
main error: expected gather → predicted work
```

This indicated a mild work bias in the survival adapter.

To address this, failure-driven augmentation was applied to the survival dataset. The augmentation focused on the region where the v1 adapter made mistakes:

```text
medium food
+ high food price
+ high scarcity
+ high deaths
=> expected gather
```

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

---

## 3. Adapter Paths

| Adapter | Path | Notes |
|---|---|---|
| Survival v1 | `adapters/qwen3_8b_survival` | Baseline Qwen3-8B survival adapter |
| Survival v2 | `adapters/qwen3_8b_survival_v2` | Failure-driven augmented survival adapter |

Both adapters use the same base model:

```text
Qwen/Qwen3-8B
```

---

## 4. Evaluation Method

The comparison used lightweight validation probes from:

```text
smoke_tests/fine_tuned_valid_probe.py
```

Each probe sampled:

```text
10 gather examples
10 work examples
20 total examples
```

This is not the final policy evaluation. It is a lightweight adapter behavior check used to compare candidate checkpoints.

---

## 5. Results

### 5.1 V1 on Original Validation Set

Command:

```bash
python smoke_tests/fine_tuned_valid_probe.py \
  --adapter-path adapters/qwen3_8b_survival \
  --data data/lora/survival/valid.jsonl \
  --samples-per-action 10
```

Result:

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

---

### 5.2 V2 on Original Validation Set

Command:

```bash
python smoke_tests/fine_tuned_valid_probe.py \
  --adapter-path adapters/qwen3_8b_survival_v2 \
  --data data/lora/survival/valid.jsonl \
  --samples-per-action 10
```

Result:

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

---

### 5.3 V2 on Augmented / V2 Validation Set

Command:

```bash
python smoke_tests/fine_tuned_valid_probe.py \
  --adapter-path adapters/qwen3_8b_survival_v2 \
  --data data/lora_v2/survival/valid.jsonl \
  --samples-per-action 10
```

Result:

```text
Accuracy: 70.00%
Expected gather: 10
Expected work:   10
```

Interpretation:

The augmented validation split is harder because it contains more boundary-focused synthetic examples. V2 did not fully solve this harder stress set.

---

### 5.4 V1 on Augmented / V2 Validation Set

Command:

```bash
python smoke_tests/fine_tuned_valid_probe.py \
  --adapter-path adapters/qwen3_8b_survival \
  --data data/lora_v2/survival/valid.jsonl \
  --samples-per-action 10
```

Result:

```text
Accuracy: 70.00%
Expected work:   10
Expected gather: 10
Predicted gather: 10
Predicted work:   10
```

Confusion summary:

```text
expected=gather predicted=gather count=7
expected=gather predicted=work   count=3
expected=work   predicted=gather count=3
expected=work   predicted=work   count=7
```

Interpretation:

V1 and V2 both reached `70%` on the augmented validation set. This suggests that the augmented validation split behaves like a harder boundary-focused stress set rather than showing a clear v2 regression.

---

## 6. Decision

The selected current best survival adapter is:

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

The v2 adapter should be used as the current best survival checkpoint:

```text
adapters/qwen3_8b_survival_v2
```

---

## 7. Notes

The v2 augmentation helped the original teacher-guided validation behavior but did not completely solve the harder augmented boundary split.

A future v3 dataset may be considered only if full simulation-level evaluation still shows survival-policy weaknesses.

For now, v2 is good enough to proceed to the next adapters.

---

## 8. Next Step

Proceed to training the remaining Qwen3-8B adapters:

```text
adapters/qwen3_8b_social_welfare
adapters/qwen3_8b_wealth_maximizing
```

The same validation-probe process should be repeated for each adapter before selecting final checkpoints.
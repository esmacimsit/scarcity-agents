# LoRA Inference Smoke Test

## 1. Purpose

This document records the LoRA inference smoke test result for the AI Society project.

The goal of this test is not to evaluate final policy quality. The goal is to verify that the local MLX-LM inference pipeline can:

```text
load the base Qwen3 model
load the saved LoRA adapter
generate an output from a regime-specific prompt
run without adapter-path or model-loading errors
```

This test was performed after a short smoke LoRA training run on the survival dataset.

---

## 2. Smoke Adapter

Base model:

```text
Qwen/Qwen3-0.6B
```

Adapter path:

```text
adapters/smoke_survival_qwen3_06b
```

Dataset used for smoke training:

```text
data/lora/survival
```

Smoke training configuration:

```text
fine-tune type: lora
iterations: 30
batch size: 1
validation batches: 5
learning rate: 1e-5
max sequence length: 512
mask prompt: enabled
```

The adapter was trained only as a toolchain test. It is not intended to be used as the final policy adapter.

---

## 3. Inference Smoke Command

The inference smoke script was run with:

```bash
python smoke_tests/lora_inference.py
```

The script tested two survival-regime prompts:

```text
1. critical_food_survival_should_gather
2. safe_food_low_coin_survival_should_work
```

---

## 4. Result Summary

Infrastructure result:

```text
base model load: PASS
LoRA adapter load: PASS
generation call: PASS
output returned: PASS
memory usage: approximately 1.5 GB
```

Behavioral hint result:

| Case | Expected Hint | Normalized Output | Result |
|---|---|---|---|
| `critical_food_survival_should_gather` | `gather` | `work` | mismatch |
| `safe_food_low_coin_survival_should_work` | `work` | `work` | match |

---

## 5. Raw Observations

For the critical-food case, the model returned:

```text
<think>

</think>

work
```

For the safe-food / low-coin case, the model returned:

```text
<think>

</think>

work
```

The Qwen3 output included an empty `<think>` block before the final answer.

---

## 6. Interpretation

The smoke inference test passed as an infrastructure test.

It confirmed that:

```text
MLX-LM can load the Qwen3-0.6B base model
MLX-LM can load the saved LoRA adapter
adapter-backed generation runs successfully
outputs can be parsed into gather/work-style actions
```

The behavioral mismatch in the critical-food case is not treated as a failure of the final method because this adapter was trained only for 30 iterations on a smoke setup.

The smoke adapter is not expected to learn robust survival behavior. Its purpose is to validate the training and inference pipeline before running the final Qwen3-8B adapter training.

---

## 7. Important Note for the Report

This smoke test should be described as a pipeline validation step, not as a model-quality evaluation.

Report wording:

```text
The LoRA smoke training and inference pipeline successfully loaded the Qwen3-0.6B base model, applied the saved adapter, and generated outputs from adapter-backed prompts. The smoke adapter was not used as a quality benchmark; one behavioral probe failed, confirming that final behavior evaluation should be performed only after full Qwen3-8B adapter training.
```

---

## 8. Next Step

The next step is to move from smoke testing to the actual final adapter training plan:

```text
Qwen3-8B survival adapter
Qwen3-8B social_welfare adapter
Qwen3-8B wealth_maximizing adapter
```

Before final evaluation, inference prompts should explicitly request a one-word output:

```text
Do not think step by step.
Do not explain.
Return only one word: gather or work.
```

This is useful because Qwen3 may emit `<think>` blocks unless the prompt strongly constrains the output format.
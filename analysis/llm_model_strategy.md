# LLM Model Strategy

## 1. Purpose

This document explains the LLM choices used in the AI Society fine-tuning pipeline.

The project uses multiple LLMs for different roles instead of relying on a single model for every stage.

The main stages are:

```text
teacher labeling
→ smoke-test fine-tuning
→ final student adapter training
```

Each model has a different responsibility.

---

## 2. Overall Model Roles

| Role | Model | Purpose |
|---|---|---|
| Teacher model | `Qwen/Qwen3-235B-A22B-Instruct-2507:novita` | Generate high-quality teacher-guided labels |
| Smoke-test model | `Qwen/Qwen3-0.6B` | Verify the MLX-LM LoRA pipeline quickly |
| Final student model | `Qwen/Qwen3-8B` | Train the actual regime-specific LoRA policy adapters |
| Possible MLX fallback | `mlx-community/Qwen3-8B-4bit` | Use if local memory/runtime requires quantized MLX weights |

---

## 3. Teacher Model

The teacher model used for dataset generation is:

```text
Qwen/Qwen3-235B-A22B-Instruct-2507:novita
```

It was accessed through Hugging Face Inference Providers.

The teacher model was used only for labeling synthetic economy states.

For each generated state, the teacher receives:

```text
regime description
+ economy state
+ allowed actions
```

The teacher returns exactly one action:

```text
gather
work
```

The teacher output is not trusted blindly. Every teacher label is filtered through deterministic validators before it becomes part of the accepted training dataset.

---

## 4. Why Use a Large Teacher Model

The action policy is not a simple one-rule classifier.

The model must learn different behavior styles:

```text
survival          → balanced survival behavior
social_welfare    → society-aware scarcity reduction
wealth_maximizing → self-interested wealth behavior
```

A large teacher model is useful because it can label ambiguous medium-risk states better than a purely hardcoded rule system.

However, validator guardrails prevent the teacher from violating core regime logic.

This creates a hybrid dataset generation pipeline:

```text
synthetic state generation
+ large teacher labeling
+ deterministic validation
+ duplicate/conflict checks
+ strict regime-level thresholds
```

---

## 5. Smoke-Test Model

The smoke-test model should be:

```text
Qwen/Qwen3-0.6B
```

The purpose of the smoke model is not final policy quality.

The smoke test is a toolchain validation step, not a model-quality experiment. It does not try to prove that a 0.6B model can learn the final policy well. It only checks whether the local training stack can consume the converted dataset and produce a usable adapter artifact.

It is used to verify that:

```text
MLX-LM can load a Qwen3 model
MLX-LM can read the chat-style JSONL dataset
train/valid files are correctly formatted
LoRA training starts correctly
prompt masking works
adapter files are saved
validation loss is computed
```

This keeps the first training test fast and cheap.

The smoke test should use a small number of iterations, for example:

```text
30 iterations
batch size 1
survival dataset only
```

A successful smoke test means that the following pipeline is functional:

```text
chat-style JSONL dataset
→ MLX-LM data loader
→ Qwen3 tokenizer/chat handling
→ LoRA training loop
→ adapter save/load path
→ validation loss computation
```

It does not mean the smoke adapter is the final policy model.

---

## 6. Final Student Model

The intended final student/base model is:

```text
Qwen/Qwen3-8B
```

The project will train three separate LoRA adapters:

```text
survival adapter
social_welfare adapter
wealth_maximizing adapter
```

Each adapter uses the same base model but a different regime-specific training dataset.

Expected adapter layout:

```text
adapters/qwen3_8b_survival
adapters/qwen3_8b_social_welfare
adapters/qwen3_8b_wealth_maximizing
```

---

## 7. Why Stay in the Qwen3 Family

The pipeline intentionally keeps the teacher, smoke-test model, and final student model within the Qwen3 family.

Model roles:

```text
teacher: Qwen3-235B-A22B
smoke:   Qwen3-0.6B
student: Qwen3-8B
```

This is useful for several reasons.

This choice is especially important because the project uses teacher-student distillation-style supervision: a large Qwen3 teacher creates the labels, and a smaller Qwen3 student is trained to imitate regime-specific decisions. Keeping the models in the same family reduces unnecessary mismatch between the label-generation model and the adapter-training model.

### 7.1 Tokenizer Compatibility

Models within the same family are more likely to use the same or highly compatible tokenizer behavior.

This reduces mismatch around:

```text
special tokens
chat message formatting
short assistant answers
system/user/assistant structure
```

### 7.2 Chat Template Compatibility

The dataset uses chat-style JSONL:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "gather"}
  ]
}
```

Keeping the models in the same family reduces the chance that the teacher labeling format and student fine-tuning format behave differently.

### 7.3 Cleaner Teacher-Student Transfer

The teacher and student are not the same size, but they share the same model family.

This can make the teacher-student setup more consistent in terms of:

```text
instruction-following style
short-answer behavior
decision formatting
chat-style interaction
```

This does not guarantee better accuracy by itself, but it is a cleaner design choice than mixing unrelated model families.

### 7.4 Stronger Report Justification

The strategy can be described as:

```text
To reduce tokenizer, chat-template, and instruction-following mismatches between teacher labeling and student fine-tuning, the pipeline keeps the teacher, smoke-test, and final adapter base models within the Qwen3 family.
```

### 7.5 Why the Smoke Model Can Differ from the Final Model

The smoke model and final student model do not need to have the same parameter size.

The smoke model is intentionally small because it is used only to test the training pipeline quickly. Moving from Qwen3-0.6B to Qwen3-8B is acceptable because the smoke test validates infrastructure and data compatibility, not final model behavior.

The important consistency point is not identical parameter count. The important point is that both models remain in the Qwen3 family, which keeps tokenizer and chat-format assumptions aligned.

---

## 8. Dataset Status

The final teacher-guided dataset checkpoint is:

```text
survival:          500 accepted / 1 rejected / 99.8% acceptance
social_welfare:    500 accepted / 9 rejected / 98.2% acceptance
wealth_maximizing: 500 accepted / 1 rejected / 99.8% acceptance

global:            1500 accepted / 11 rejected / 99.3% acceptance
strict status:     PASS
```

The dataset was converted into LoRA train/validation format:

```text
survival:          450 train / 50 valid
social_welfare:    450 train / 50 valid
wealth_maximizing: 450 train / 50 valid
```

Total converted examples:

```text
1350 train
150 valid
1500 total
```

---

## 9. Training Strategy

The planned training sequence is:

```text
1. Run Qwen3-0.6B smoke LoRA on the survival dataset
2. Verify adapter files are saved
3. Run a small inference test with the smoke adapter
4. Train Qwen3-8B survival adapter
5. Train Qwen3-8B social_welfare adapter
6. Train Qwen3-8B wealth_maximizing adapter
7. Evaluate the three adapters against the existing policy comparison workflow
```

The smoke test is intentionally small.

The final adapters should use the validated 500-per-regime dataset.

---

## 10. Fallback Plan

If Qwen3-8B is too heavy for the local Apple Silicon setup, the fallback is:

```text
mlx-community/Qwen3-8B-4bit
```

If that is still too slow or memory-heavy, a smaller Qwen3-family model can be used for the thesis demonstration.

The fallback should preserve the same model family when possible.

---

## 11. Report-Ready Summary

The project uses a three-stage Qwen3-based LLM strategy.

A large Qwen3 teacher model generates high-quality labels for synthetic economy states. These labels are filtered with deterministic validators and strict dataset checks.

A small Qwen3 model is used first as a smoke-test target to verify that the LoRA training pipeline can read the converted dataset and save adapters correctly.

The final planned student model is Qwen3-8B, trained with three separate LoRA adapters for survival, social welfare, and wealth-maximizing policies.

This design keeps the teacher, smoke-test, and final adapter models within the same model family to reduce tokenizer, chat-template, and instruction-following mismatches.


# Fine-Tune Dataset Generation Path

## 1. Objective

The goal of this pipeline is to create a small but high-quality teacher-guided seed dataset for fine-tuning regime-specific LoRA adapters in the AI Society project.

The objective is not to generate the largest possible dataset directly from the teacher model. Instead, the teacher is used as a high-quality decision oracle for a controlled seed dataset. This seed dataset can later be expanded with synthetic augmentation and additional validation.

The target behavior regimes are:

- `survival`
- `social_welfare`
- `wealth_maximizing`

Each regime learns a different action policy over the same scarcity-based economy state space.

---

## 2. Teacher Model

The current teacher model is:

```text
Qwen/Qwen3-235B-A22B-Instruct-2507:novita
```

The teacher is accessed through Hugging Face Inference Providers.

The teacher labels each generated economy state with exactly one action:

```text
gather
work
```

The teacher output is not accepted blindly. Every generated label is filtered through deterministic validation rules before being written to the accepted dataset.

---

## 3. Why Teacher-Guided Seed Data

The project uses teacher-guided generation because the desired behavior is not a simple one-rule classifier.

Each regime needs a different decision style:

- `survival`: balanced, survival-oriented behavior
- `social_welfare`: society-aware behavior that reacts strongly to scarcity, deaths, and high prices
- `wealth_maximizing`: self-interested behavior that prioritizes work/wealth when personal survival is safe

The teacher helps label ambiguous medium-risk states where hardcoded rules alone would be too crude.

The validators provide guardrails so that the teacher cannot produce labels that violate core regime logic.

---

## 4. Economy State Schema

Each generated example contains one synthetic economy state.

Current state fields:

```text
example_id
regime
timestep
food
coin
productivity
wealth
food_price
alive_count
dead_total
total_food
scarcity_ratio
```

The output label is:

```text
action: gather | work
```

---

## 5. Regime-Specific State Generation

The state generator uses deterministic regime-specific scenario cycles rather than fully random sampling.

This prevents small validation runs from missing important edge cases by chance.

Scenario types:

```text
safe
medium
scarce
critical
```

### `survival`

The survival regime receives a balanced mix of safe, medium, scarce, and critical states.

Purpose:

- teach `gather` when food is critical or scarcity is high
- teach `work` when food is safe and coin is low
- keep the policy balanced rather than purely gather-heavy

### `social_welfare`

The social welfare regime receives more scarce and critical states.

Purpose:

- expose the model to high scarcity
- expose the model to high death count
- expose the model to high food price
- encourage gather-heavy behavior under society-level crisis

### `wealth_maximizing`

The wealth-maximizing regime receives more safe and medium states, with enough critical states to preserve survival guardrails.

Purpose:

- teach work-heavy self-interested behavior
- avoid turning wealth maximization into social welfare behavior
- still teach gather when personal survival is at risk

The intended behavior is:

```text
selfish but not suicidal
```

---

## 6. Teacher Prompting

For each batch, the teacher receives:

- the target behavior regime
- a short regime description
- a list of synthetic economy states
- the allowed actions: `gather`, `work`
- strict output format instructions

The teacher must return valid JSON only.

Expected response format:

```json
[
  {"example_id": "...", "action": "gather"},
  {"example_id": "...", "action": "work"}
]
```

The parser accepts a direct JSON array and also tolerates accidental surrounding text by extracting the first JSON array from the teacher response.

---

## 7. Validator Guardrails

Teacher labels are filtered by deterministic validators.

### Shared rule

Invalid actions are rejected.

```text
action must be gather or work
```

### `survival`

Hard guardrails:

- if `food <= 2.0`, action must be `gather`
- if food is safe, coin is low, food price is low, and scarcity is low, action should be `work`

### `social_welfare`

Hard guardrails:

- if food price is high and scarcity is high, action must be `gather`
- if deaths are high and scarcity is high, action must be `gather`

### `wealth_maximizing`

Hard guardrails:

- if `food <= 2.0`, action must be `gather`
- if food is safe and coin is low, action should be `work`
- if food is safe and cheap, action should be `work`

These validators ensure that the teacher can label ambiguous cases, but cannot violate core regime semantics.

---

## 8. Output Files

For each regime, the generator writes files under:

```text
data/finetune/<regime>/
```

Current files:

```text
teacher_guided_accepted.jsonl
teacher_guided_rejected.jsonl
teacher_guided_batches.jsonl
teacher_guided_cache.jsonl
```

### `teacher_guided_accepted.jsonl`

Contains accepted examples after teacher labeling and validator filtering.

These are the candidate examples for fine-tuning.

### `teacher_guided_rejected.jsonl`

Contains rejected teacher labels and rejection reasons.

This file is useful for debugging teacher drift and overly risky labels.

### `teacher_guided_batches.jsonl`

Contains batch-level teacher prompts and raw teacher responses.

This avoids storing the same teacher response repeatedly for every state.

### `teacher_guided_cache.jsonl`

Contains cache entries keyed by state signature.

This prevents repeated teacher calls for states that were already processed.

---

## 9. Cache and Resume Strategy

Large runs should use resume mode:

```bash
python scripts/generate_finetune_dataset.py --examples-per-regime 300 --batch-size 10 --resume
```

The cache key is based on the generated state, excluding `example_id`.

Resume mode uses the cache length as the generated-state count. This prevents the generator from restarting at the first seeded states and appending duplicate examples.

Resume mode also advances the deterministic RNG by replaying already-generated states before producing new states.

This was explicitly tested because an earlier version reused the first cached states during resume and duplicated accepted examples.

The corrected behavior is that cache size increases during resume:

```text
cache=10 → cache=15 → cache=20
```

---

## 10. Duplicate and Conflict Checks

The validation script computes stable state signatures for accepted examples.

The signature excludes `example_id` and rounds float values to reduce formatting noise.

The validator checks for:

- duplicate state signatures
- conflicting duplicate labels

Strict validation fails if duplicates are found.

This is important because repeated states can make the LoRA adapter memorize examples rather than learn regime behavior.

---

## 11. Strict Validation Thresholds

The validation script supports strict mode:

```bash
python scripts/validate_finetune_dataset.py --strict --min-examples 20
```

Strict validation checks:

### `survival`

- gather ratio must stay between `0.35` and `0.65`
- critical-food gather ratio must be `1.0`

### `social_welfare`

- gather ratio must be at least `0.50`
- high-scarcity gather ratio must be at least `0.70`
- critical-food gather ratio must be `1.0`

### `wealth_maximizing`

- work ratio must be at least `0.70`
- gather ratio must be at least `0.05`
- critical-food gather ratio must be `1.0`

Strict validation also fails if:

- accepted examples are below the requested minimum
- critical-food coverage is missing
- safe-food coverage is missing
- high-scarcity coverage is missing
- duplicate states are found
- conflicting duplicate labels are found

---

## 12. Small Integration Test Result

A small integration test was run after adding:

- cache/resume
- batch-level raw logging
- duplicate/conflict checks
- strict validation thresholds
- deterministic regime-specific state generation

Test command:

```bash
python scripts/generate_finetune_dataset.py --examples-per-regime 10 --batch-size 5
python scripts/generate_finetune_dataset.py --examples-per-regime 20 --batch-size 5 --resume
python scripts/validate_finetune_dataset.py --strict --min-examples 20
```

Result:

```text
survival:          20 accepted / 1 rejected / 95.2% acceptance
social_welfare:    20 accepted / 0 rejected / 100.0% acceptance
wealth_maximizing: 20 accepted / 0 rejected / 100.0% acceptance

global:            60 accepted / 1 rejected / 98.4% acceptance
strict status:     PASS
```

Resume behavior was also verified.

The cache increased during resume instead of staying fixed:

```text
survival:          cache=15 → cache=20 → cache=25
social_welfare:    cache=10 → cache=15 → cache=20
wealth_maximizing: cache=10 → cache=15 → cache=20
```

This confirms that resume no longer reuses the same initial cached states.

---

## 13. Current Status

The dataset generation pipeline has passed the small integration test.

Completed items:

```text
[x] cache/resume
[x] batch raw log separation
[x] duplicate/conflict check
[x] strict validation thresholds
[x] regime-specific targeted state generation
[x] small integration test
[x] strict validation PASS
```

This pipeline is now ready for the next controlled dataset run.

---

## 14. Recommended Next Step

Do not jump directly to a very large dataset.

Recommended next step:

```bash
python scripts/generate_finetune_dataset.py --examples-per-regime 100 --batch-size 10
python scripts/validate_finetune_dataset.py --strict --min-examples 100
```

If that passes, continue to:

```bash
python scripts/generate_finetune_dataset.py --examples-per-regime 300 --batch-size 10 --resume
python scripts/validate_finetune_dataset.py --strict --min-examples 300
```

Only after strict validation passes at this scale should the project move toward final train/validation conversion and LoRA adapter training.

---

## 15. Notes for the Thesis / Report

This method can be described as a hybrid teacher-guided dataset generation pipeline.

The important design point is that the teacher model does not directly define the final dataset alone.

Instead, the pipeline combines:

```text
synthetic economy state generation
+ teacher-guided action labeling
+ deterministic validator guardrails
+ cache/resume safety
+ duplicate/conflict detection
+ strict regime-level validation
```

This makes the dataset more defensible than using raw synthetic labels directly from a single LLM.
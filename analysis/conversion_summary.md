# LoRA Dataset Conversion Summary

Teacher-guided accepted examples were converted into chat-style LoRA train/validation JSONL files.

This conversion uses the validated 500-per-regime teacher-guided dataset checkpoint.

## Dataset Checkpoint

```text
survival:          500 accepted / 1 rejected / 99.8% acceptance
social_welfare:    500 accepted / 9 rejected / 98.2% acceptance
wealth_maximizing: 500 accepted / 1 rejected / 99.8% acceptance

global:            1500 accepted / 11 rejected / 99.3% acceptance
strict status:     PASS
```

## Conversion Format

Each converted example uses chat-style JSONL format:

```json
{
  "messages": [
    {"role": "system", "content": "...regime instruction..."},
    {"role": "user", "content": "...economy state..."},
    {"role": "assistant", "content": "gather"}
  ],
  "metadata": {
    "source": "teacher_guided",
    "teacher_model": "Qwen/Qwen3-235B-A22B-Instruct-2507:novita",
    "regime": "survival",
    "example_id": "survival_00001",
    "action": "gather"
  }
}
```

The assistant output is always exactly one action:

```text
gather
work
```

## Train / Validation Split

Validation ratio: `10%`

| Regime | Total | Train | Valid | Gather | Work |
|---|---:|---:|---:|---:|---:|
| `survival` | 500 | 450 | 50 | 218 | 282 |
| `social_welfare` | 500 | 450 | 50 | 346 | 154 |
| `wealth_maximizing` | 500 | 450 | 50 | 135 | 365 |

## Regime Behavior Pattern

The action distributions show the intended policy separation:

```text
social_welfare    -> most gather-heavy
survival          -> balanced but slightly work-heavy
wealth_maximizing -> most work-heavy
```

This confirms that the converted LoRA datasets preserve the behavioral differences learned from the teacher-guided seed dataset.

## Output Paths

### `survival`

- Train: `data/lora/survival/train.jsonl`
- Valid: `data/lora/survival/valid.jsonl`

### `social_welfare`

- Train: `data/lora/social_welfare/train.jsonl`
- Valid: `data/lora/social_welfare/valid.jsonl`

### `wealth_maximizing`

- Train: `data/lora/wealth_maximizing/train.jsonl`
- Valid: `data/lora/wealth_maximizing/valid.jsonl`

## Notes

The generated JSONL train/validation files are ignored by Git because they are derived dataset artifacts.

The summary file is safe to commit because it documents the conversion result without storing the full training data.
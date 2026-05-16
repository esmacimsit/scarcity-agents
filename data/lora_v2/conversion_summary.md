# LoRA Dataset Conversion Summary

Teacher-guided accepted examples were converted into chat-style LoRA train/validation JSONL files.

| Regime | Total | Train | Valid | Gather | Work |
|---|---:|---:|---:|---:|---:|
| `survival` | 850 | 765 | 85 | 468 | 382 |

## Output Paths

### `survival`

- Input: `data/finetune/survival/survival_combined_accepted.jsonl`
- Train: `data/lora_v2/survival/train.jsonl`
- Valid: `data/lora_v2/survival/valid.jsonl`

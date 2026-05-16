# LoRA Dataset Conversion Summary

Teacher-guided accepted examples were converted into chat-style LoRA train/validation JSONL files.

| Regime | Total | Train | Valid | Gather | Work |
|---|---:|---:|---:|---:|---:|
| `wealth_maximizing` | 650 | 585 | 65 | 235 | 415 |

## Output Paths

### `wealth_maximizing`

- Input: `data/finetune/wealth_maximizing/wealth_combined_accepted.jsonl`
- Train: `data/lora_v2/wealth_maximizing/train.jsonl`
- Valid: `data/lora_v2/wealth_maximizing/valid.jsonl`

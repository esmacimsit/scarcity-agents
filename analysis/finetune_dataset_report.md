# Fine-Tune Dataset Validation Report

This report summarizes the current teacher-guided fine-tune dataset.

The dataset is generated from synthetic economy states labeled by a Qwen teacher model and filtered by regime-specific validators.

## Regime: `survival`

Accepted examples: **20**
Rejected examples: **1**
Total generated/seen examples: **21**
Acceptance rate: **95.2%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.650 |
| `work_ratio` | 0.350 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 1.000 |
| `critical_food_total` | 5 |
| `high_scarcity_total` | 9 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 13 | 65.0% |
| `work` | 7 | 35.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 5 | 25.0% |
| `low_food_2_4` | 4 | 20.0% |
| `medium_food_4_7` | 4 | 20.0% |
| `safe_food_>7` | 7 | 35.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 5 | 25.0% |
| `high_scarcity_1.7_2.4` | 4 | 20.0% |
| `low_scarcity_<=1.1` | 7 | 35.0% |
| `medium_scarcity_1.1_1.7` | 4 | 20.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 4 | 20.0% |
| `high_price_5_7.5` | 5 | 25.0% |
| `low_price_<=2.5` | 6 | 30.0% |
| `medium_price_2.5_5` | 5 | 25.0% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 20 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `survival_safe_low_coin_allows_work` | 1 | 100.0% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Regime: `social_welfare`

Accepted examples: **20**
Rejected examples: **0**
Total generated/seen examples: **20**
Acceptance rate: **100.0%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.850 |
| `work_ratio` | 0.150 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 1.000 |
| `critical_food_total` | 6 |
| `high_scarcity_total` | 14 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 17 | 85.0% |
| `work` | 3 | 15.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 6 | 30.0% |
| `low_food_2_4` | 4 | 20.0% |
| `medium_food_4_7` | 7 | 35.0% |
| `safe_food_>7` | 3 | 15.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 7 | 35.0% |
| `high_scarcity_1.7_2.4` | 7 | 35.0% |
| `low_scarcity_<=1.1` | 2 | 10.0% |
| `medium_scarcity_1.1_1.7` | 4 | 20.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 3 | 15.0% |
| `high_price_5_7.5` | 9 | 45.0% |
| `low_price_<=2.5` | 2 | 10.0% |
| `medium_price_2.5_5` | 6 | 30.0% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 20 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| none | 0 | 0.0% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Regime: `wealth_maximizing`

Accepted examples: **20**
Rejected examples: **0**
Total generated/seen examples: **20**
Acceptance rate: **100.0%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.250 |
| `work_ratio` | 0.750 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.833 |
| `critical_food_total` | 4 |
| `high_scarcity_total` | 6 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 5 | 25.0% |
| `work` | 15 | 75.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 4 | 20.0% |
| `low_food_2_4` | 2 | 10.0% |
| `medium_food_4_7` | 6 | 30.0% |
| `safe_food_>7` | 8 | 40.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 4 | 20.0% |
| `high_scarcity_1.7_2.4` | 2 | 10.0% |
| `low_scarcity_<=1.1` | 9 | 45.0% |
| `medium_scarcity_1.1_1.7` | 5 | 25.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 3 | 15.0% |
| `high_price_5_7.5` | 3 | 15.0% |
| `low_price_<=2.5` | 9 | 45.0% |
| `medium_price_2.5_5` | 5 | 25.0% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 20 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| none | 0 | 0.0% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Global Summary

Total accepted examples: **60**
Total rejected examples: **1**
Total seen examples: **61**
Global acceptance rate: **98.4%**
Strict validation status: **PASS**

### Global Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 35 | 58.3% |
| `work` | 25 | 41.7% |

### Next Steps

- If strict validation passes, generate a larger teacher-guided dataset.
- If a regime has poor coverage, generate more targeted states for that regime.
- Keep teacher labels validator-filtered before training LoRA adapters.

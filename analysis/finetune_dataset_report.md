# Fine-Tune Dataset Validation Report

This report summarizes the current teacher-guided fine-tune dataset.

The dataset is generated from synthetic economy states labeled by a Qwen teacher model and filtered by regime-specific validators.

## Regime: `survival`

Accepted examples: **300**
Rejected examples: **0**
Total generated/seen examples: **300**
Acceptance rate: **100.0%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.433 |
| `work_ratio` | 0.567 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 1.000 |
| `critical_food_total` | 60 |
| `high_scarcity_total` | 120 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 130 | 43.3% |
| `work` | 170 | 56.7% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 60 | 20.0% |
| `low_food_2_4` | 34 | 11.3% |
| `medium_food_4_7` | 91 | 30.3% |
| `safe_food_>7` | 115 | 38.3% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 70 | 23.3% |
| `high_scarcity_1.7_2.4` | 50 | 16.7% |
| `low_scarcity_<=1.1` | 105 | 35.0% |
| `medium_scarcity_1.1_1.7` | 75 | 25.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 44 | 14.7% |
| `high_price_5_7.5` | 63 | 21.0% |
| `low_price_<=2.5` | 101 | 33.7% |
| `medium_price_2.5_5` | 92 | 30.7% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 300 |
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

## Regime: `social_welfare`

Accepted examples: **300**
Rejected examples: **3**
Total generated/seen examples: **303**
Acceptance rate: **99.0%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.690 |
| `work_ratio` | 0.310 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.986 |
| `critical_food_total` | 92 |
| `high_scarcity_total` | 210 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 207 | 69.0% |
| `work` | 93 | 31.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 92 | 30.7% |
| `low_food_2_4` | 62 | 20.7% |
| `medium_food_4_7` | 107 | 35.7% |
| `safe_food_>7` | 39 | 13.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 102 | 34.0% |
| `high_scarcity_1.7_2.4` | 108 | 36.0% |
| `low_scarcity_<=1.1` | 36 | 12.0% |
| `medium_scarcity_1.1_1.7` | 54 | 18.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 76 | 25.3% |
| `high_price_5_7.5` | 111 | 37.0% |
| `low_price_<=2.5` | 39 | 13.0% |
| `medium_price_2.5_5` | 74 | 24.7% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 300 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `social_welfare_deaths_scarcity_requires_gather` | 1 | 33.3% |
| `social_welfare_high_price_scarcity_requires_gather` | 2 | 66.7% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Regime: `wealth_maximizing`

Accepted examples: **300**
Rejected examples: **1**
Total generated/seen examples: **301**
Acceptance rate: **99.7%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.253 |
| `work_ratio` | 0.747 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.789 |
| `critical_food_total` | 60 |
| `high_scarcity_total` | 90 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 76 | 25.3% |
| `work` | 224 | 74.7% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 60 | 20.0% |
| `low_food_2_4` | 23 | 7.7% |
| `medium_food_4_7` | 80 | 26.7% |
| `safe_food_>7` | 137 | 45.7% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 60 | 20.0% |
| `high_scarcity_1.7_2.4` | 30 | 10.0% |
| `low_scarcity_<=1.1` | 138 | 46.0% |
| `medium_scarcity_1.1_1.7` | 72 | 24.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 40 | 13.3% |
| `high_price_5_7.5` | 41 | 13.7% |
| `low_price_<=2.5` | 131 | 43.7% |
| `medium_price_2.5_5` | 88 | 29.3% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 300 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `wealth_safe_low_coin_prefers_work` | 1 | 100.0% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Global Summary

Total accepted examples: **900**
Total rejected examples: **4**
Total seen examples: **904**
Global acceptance rate: **99.6%**
Strict validation status: **PASS**

### Global Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 413 | 45.9% |
| `work` | 487 | 54.1% |

### Next Steps

- If strict validation passes, generate a larger teacher-guided dataset.
- If a regime has poor coverage, generate more targeted states for that regime.
- Keep teacher labels validator-filtered before training LoRA adapters.

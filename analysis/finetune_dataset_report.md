# Fine-Tune Dataset Validation Report

This report summarizes the current teacher-guided fine-tune dataset.

The dataset is generated from synthetic economy states labeled by a Qwen teacher model and filtered by regime-specific validators.

## Regime: `survival`

Accepted examples: **500**
Rejected examples: **1**
Total generated/seen examples: **501**
Acceptance rate: **99.8%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.436 |
| `work_ratio` | 0.564 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.990 |
| `critical_food_total` | 101 |
| `high_scarcity_total` | 201 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 218 | 43.6% |
| `work` | 282 | 56.4% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 101 | 20.2% |
| `low_food_2_4` | 60 | 12.0% |
| `medium_food_4_7` | 153 | 30.6% |
| `safe_food_>7` | 186 | 37.2% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 119 | 23.8% |
| `high_scarcity_1.7_2.4` | 82 | 16.4% |
| `low_scarcity_<=1.1` | 171 | 34.2% |
| `medium_scarcity_1.1_1.7` | 128 | 25.6% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 76 | 15.2% |
| `high_price_5_7.5` | 102 | 20.4% |
| `low_price_<=2.5` | 173 | 34.6% |
| `medium_price_2.5_5` | 149 | 29.8% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 500 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `missing_label_for_example_id` | 1 | 100.0% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Regime: `social_welfare`

Accepted examples: **500**
Rejected examples: **9**
Total generated/seen examples: **509**
Acceptance rate: **98.2%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.692 |
| `work_ratio` | 0.308 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.989 |
| `critical_food_total` | 154 |
| `high_scarcity_total` | 348 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 346 | 69.2% |
| `work` | 154 | 30.8% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 154 | 30.8% |
| `low_food_2_4` | 103 | 20.6% |
| `medium_food_4_7` | 175 | 35.0% |
| `safe_food_>7` | 68 | 13.6% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 177 | 35.4% |
| `high_scarcity_1.7_2.4` | 171 | 34.2% |
| `low_scarcity_<=1.1` | 64 | 12.8% |
| `medium_scarcity_1.1_1.7` | 88 | 17.6% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 124 | 24.8% |
| `high_price_5_7.5` | 191 | 38.2% |
| `low_price_<=2.5` | 64 | 12.8% |
| `medium_price_2.5_5` | 121 | 24.2% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 500 |
| `duplicate_groups` | 0 |
| `duplicate_rows` | 0 |
| `conflict_groups` | 0 |
| `conflict_rows` | 0 |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `social_welfare_deaths_scarcity_requires_gather` | 7 | 77.8% |
| `social_welfare_high_price_scarcity_requires_gather` | 2 | 22.2% |

### Warnings

- No warnings.

### Strict Failures

- No strict failures.

## Regime: `wealth_maximizing`

Accepted examples: **500**
Rejected examples: **1**
Total generated/seen examples: **501**
Acceptance rate: **99.8%**

### Strict Metrics

| Metric | Value |
|---|---:|
| `gather_ratio` | 0.270 |
| `work_ratio` | 0.730 |
| `critical_food_gather_ratio` | 1.000 |
| `high_scarcity_gather_ratio` | 0.807 |
| `critical_food_total` | 100 |
| `high_scarcity_total` | 150 |

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 135 | 27.0% |
| `work` | 365 | 73.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 100 | 20.0% |
| `low_food_2_4` | 39 | 7.8% |
| `medium_food_4_7` | 130 | 26.0% |
| `safe_food_>7` | 231 | 46.2% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 99 | 19.8% |
| `high_scarcity_1.7_2.4` | 51 | 10.2% |
| `low_scarcity_<=1.1` | 228 | 45.6% |
| `medium_scarcity_1.1_1.7` | 122 | 24.4% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 63 | 12.6% |
| `high_price_5_7.5` | 74 | 14.8% |
| `low_price_<=2.5` | 216 | 43.2% |
| `medium_price_2.5_5` | 147 | 29.4% |

### Duplicate / Conflict Check

| Metric | Value |
|---|---:|
| `unique_signatures` | 500 |
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

Total accepted examples: **1500**
Total rejected examples: **11**
Total seen examples: **1511**
Global acceptance rate: **99.3%**
Strict validation status: **PASS**

### Global Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 699 | 46.6% |
| `work` | 801 | 53.4% |

### Next Steps

- If strict validation passes, generate a larger teacher-guided dataset.
- If a regime has poor coverage, generate more targeted states for that regime.
- Keep teacher labels validator-filtered before training LoRA adapters.

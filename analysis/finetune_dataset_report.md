# Fine-Tune Dataset Validation Report

This report summarizes the current teacher-guided fine-tune dataset.

The dataset is generated from synthetic economy states labeled by a Qwen teacher model and filtered by regime-specific validators.

## Regime: `survival`

Accepted examples: **10**
Rejected examples: **0**
Total generated/seen examples: **10**
Acceptance rate: **100.0%**

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 5 | 50.0% |
| `work` | 5 | 50.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 1 | 10.0% |
| `low_food_2_4` | 1 | 10.0% |
| `medium_food_4_7` | 6 | 60.0% |
| `safe_food_>7` | 2 | 20.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 2 | 20.0% |
| `high_scarcity_1.7_2.4` | 2 | 20.0% |
| `low_scarcity_<=1.1` | 4 | 40.0% |
| `medium_scarcity_1.1_1.7` | 2 | 20.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 1 | 10.0% |
| `high_price_5_7.5` | 1 | 10.0% |
| `low_price_<=2.5` | 3 | 30.0% |
| `medium_price_2.5_5` | 5 | 50.0% |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| none | 0 | 0.0% |

### Warnings

- No warnings.

## Regime: `social_welfare`

Accepted examples: **10**
Rejected examples: **0**
Total generated/seen examples: **10**
Acceptance rate: **100.0%**

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 5 | 50.0% |
| `work` | 5 | 50.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 3 | 30.0% |
| `medium_food_4_7` | 1 | 10.0% |
| `safe_food_>7` | 6 | 60.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 2 | 20.0% |
| `high_scarcity_1.7_2.4` | 2 | 20.0% |
| `low_scarcity_<=1.1` | 6 | 60.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 2 | 20.0% |
| `high_price_5_7.5` | 1 | 10.0% |
| `low_price_<=2.5` | 6 | 60.0% |
| `medium_price_2.5_5` | 1 | 10.0% |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| none | 0 | 0.0% |

### Warnings

- No warnings.

## Regime: `wealth_maximizing`

Accepted examples: **10**
Rejected examples: **2**
Total generated/seen examples: **12**
Acceptance rate: **83.3%**

### Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 2 | 20.0% |
| `work` | 8 | 80.0% |

### Food Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `critical_food_<=2` | 1 | 10.0% |
| `low_food_2_4` | 1 | 10.0% |
| `medium_food_4_7` | 5 | 50.0% |
| `safe_food_>7` | 3 | 30.0% |

### Scarcity Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_scarcity_>2.4` | 1 | 10.0% |
| `high_scarcity_1.7_2.4` | 4 | 40.0% |
| `low_scarcity_<=1.1` | 3 | 30.0% |
| `medium_scarcity_1.1_1.7` | 2 | 20.0% |

### Food Price Coverage

| Item | Count | Ratio |
|---|---:|---:|
| `extreme_price_>7.5` | 2 | 20.0% |
| `low_price_<=2.5` | 3 | 30.0% |
| `medium_price_2.5_5` | 5 | 50.0% |

### Rejection Reasons

| Item | Count | Ratio |
|---|---:|---:|
| `wealth_food_critical_requires_gather` | 2 | 100.0% |

### Warnings

- No warnings.

## Global Summary

Total accepted examples: **30**
Total rejected examples: **2**
Total seen examples: **32**
Global acceptance rate: **93.8%**

### Global Action Distribution

| Item | Count | Ratio |
|---|---:|---:|
| `gather` | 12 | 40.0% |
| `work` | 18 | 60.0% |

### Next Steps

- If warnings are acceptable, generate a larger teacher-guided dataset.
- If a regime has poor coverage, generate more targeted states for that regime.
- Keep teacher labels validator-filtered before training LoRA adapters.

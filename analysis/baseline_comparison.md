

# Baseline Policy Comparison

This document summarizes the Chapter 1 baseline experiment results for the scarcity-based economic simulation.

The comparison focuses on two non-LLM policies:

- `random`: agents choose `gather` or `work` randomly.
- `rule`: agents use a deterministic rule-based policy based on food, coin, and food price.

The purpose of this comparison is to establish a clear non-LLM baseline before introducing any advanced decision-making policy in later stages.

---

## Experiment Setup

Each policy was evaluated across three environmental scenarios:

| Scenario | Description |
|---|---|
| `default` | Low-stress environment using the default simulation configuration. |
| `moderate_scarcity` | Medium-stress environment designed to reveal welfare loss before total collapse. |
| `scarcity` | High-stress environment designed to test policy robustness under severe resource pressure. |

Each scenario-policy pair was run across five seeds:

| Setting | Value |
|---|---:|
| Initial agents | 50 |
| Timesteps | 300 |
| Seeds | 1, 2, 3, 4, 5 |
| Policies | `random`, `rule` |
| Scenarios | `default`, `moderate_scarcity`, `scarcity` |

Total experiment runs:

| Calculation | Total |
|---|---:|
| 3 scenarios × 2 policies × 5 seeds | 30 runs |

---

## Summary Table

The following table reports the average results across five seeds for each scenario-policy pair.

| Scenario | Policy | Survival Rate | Avg. Dead | Avg. Price | Final Population Gini | Gather Ratio |
|---|---|---:|---:|---:|---:|---:|
| `default` | `random` | 1.0000 | 0.00 | 1.4599 | 0.0380 | 0.4984 |
| `default` | `rule` | 1.0000 | 0.00 | 1.3833 | 0.0304 | 0.5056 |
| `moderate_scarcity` | `random` | 0.6680 | 16.60 | 5.0442 | 0.5291 | 0.4980 |
| `moderate_scarcity` | `rule` | 1.0000 | 0.00 | 2.8420 | 0.0478 | 0.5622 |
| `scarcity` | `random` | 0.0000 | 50.00 | 9.4837 | 0.0000 | 0.4933 |
| `scarcity` | `rule` | 1.0000 | 0.00 | 3.0894 | 0.0620 | 0.7322 |

---

## Default Scenario

In the default scenario, both policies achieved full survival.

| Policy | Survival Rate | Avg. Dead | Avg. Price | Final Population Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 1.0000 | 0.00 | 1.4599 | 0.0380 | 0.4984 |
| `rule` | 1.0000 | 0.00 | 1.3833 | 0.0304 | 0.5056 |

This indicates that the default environment is relatively low-stress. Random behavior is sufficient for survival because the resource pressure is not strong enough to expose major differences between policies.

However, the rule-based policy still produced slightly lower average price and lower population-level inequality. This suggests that even in easy settings, a simple state-aware policy can lead to a more stable economy.

**Interpretation:**  
The default scenario is useful as a sanity check, but it is not difficult enough to evaluate policy robustness.

---

## Moderate Scarcity Scenario

The moderate scarcity scenario creates a clearer separation between policies.

| Policy | Survival Rate | Avg. Dead | Avg. Price | Final Population Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.6680 | 16.60 | 5.0442 | 0.5291 | 0.4980 |
| `rule` | 1.0000 | 0.00 | 2.8420 | 0.0478 | 0.5622 |

Under moderate scarcity, the random policy did not collapse completely, but it showed clear signs of economic stress:

- survival dropped to 66.8%
- average deaths increased to 16.6 agents
- average food price increased sharply
- population-level inequality increased significantly
- gather ratio stayed close to random behavior

The rule-based policy avoided deaths entirely while maintaining a lower average price and much lower population-level inequality. It also increased the gather ratio compared to the default setting, showing a basic form of scarcity-aware adaptation.

**Interpretation:**  
This scenario captures the difference between survival and welfare. Random agents may partially survive, but the population experiences strong economic pressure and inequality. The rule-based policy provides a more stable and adaptive baseline.

---

## Scarcity Scenario

The scarcity scenario produces the strongest policy separation.

| Policy | Survival Rate | Avg. Dead | Avg. Price | Final Population Gini | Gather Ratio |
|---|---:|---:|---:|---:|---:|
| `random` | 0.0000 | 50.00 | 9.4837 | 0.0000 | 0.4933 |
| `rule` | 1.0000 | 0.00 | 3.0894 | 0.0620 | 0.7322 |

In this high-stress setting, the random policy collapsed across all seeds. All agents died by the end of the simulation, and the food price approached the configured upper bound.

In contrast, the rule-based policy maintained full survival across all seeds. The gather ratio increased to 0.7322, indicating that agents shifted strongly toward food production under severe scarcity.

**Interpretation:**  
Severe scarcity exposes the weakness of non-adaptive random behavior. The rule-based policy survives because it reacts to low food and high prices by prioritizing food production.

---

## Key Findings

### 1. The default scenario is too easy to expose strong policy differences

Both random and rule-based agents survived in the default scenario. This confirms that the base environment is stable and suitable as a sanity-check setting.

### 2. Moderate scarcity reveals welfare loss before total collapse

The random policy partially survived in the moderate scarcity scenario, but survival alone did not reflect the full system condition. Average price and population-level Gini increased sharply, showing that the system experienced economic suffering even before total collapse.

### 3. Random behavior fails under stronger scarcity

In the scarcity scenario, random agents failed completely. The policy did not adapt its action distribution, keeping gather behavior near 50%, which was insufficient under severe resource pressure.

### 4. Rule-based behavior provides a strong non-LLM baseline

The rule-based policy preserved full survival across all scenarios. It also increased gather behavior as scarcity intensified, suggesting that even a simple state-aware strategy can stabilize the environment.

### 5. Survival alone is not enough

The moderate scarcity results show that a policy can avoid immediate total collapse while still producing high inequality, high price pressure, and partial population loss. Therefore, survival must be interpreted together with welfare-oriented metrics.

---

## Chapter 1 Conclusion

The Chapter 1 baseline experiments show that policy behavior matters significantly under scarcity.

In low-stress settings, random and rule-based policies may appear similar. However, as resource pressure increases, random behavior becomes unstable and eventually collapses. The rule-based policy remains resilient because it reacts to food scarcity and high prices by increasing food production.

These results establish a clear non-LLM baseline for later comparison. Any future advanced policy should be evaluated against both the random baseline and the rule-based baseline, especially under `moderate_scarcity` and `scarcity` scenarios.

---

## Transition to Later Stages

Chapter 1 establishes the simulation environment, stress scenarios, evaluation metrics, and non-LLM baselines.

Later stages can compare advanced decision-making policies against these baselines using the same scenarios and metrics.

The most important future questions are:

- Can an advanced policy detect scarcity from the same environment state?
- Can it increase gather behavior before collapse?
- Can it reduce deaths, price pressure, and inequality under moderate or severe scarcity?
- Can it perform better than random behavior while remaining competitive with the rule-based baseline?
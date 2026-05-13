# Evaluation Metrics

This document defines the metrics used to evaluate agent behavior in the scarcity-based economic simulation.

The goal of these metrics is not only to measure whether agents survive, but also to capture economic pressure, inequality, market instability, and behavioral adaptation under different scarcity scenarios.

## Why Metrics Matter

A simple survival count is not enough to evaluate the quality of an agent policy.

An agent population may survive while still experiencing:

- high food prices
- unstable market conditions
- high inequality
- strong dependency on trade
- poor adaptation to scarcity

For this reason, the simulation tracks both survival-oriented and welfare-oriented metrics.

In this project:

```text
Survival ≠ Welfare
```

Survival measures whether agents remain alive. Welfare-related metrics describe how stable, fair, and sustainable the simulated economy is.

---

## Survival Rate

**Definition:**  
The proportion of agents alive at the end of the simulation.

```text
survival_rate = final_alive / initial_population
```

**Interpretation:**  
A higher survival rate means that a policy is better at keeping agents alive under the given scenario.

**Why it matters:**  
This is the most direct measure of whether a policy can handle scarcity pressure.

**Example interpretation:**

- `1.0` means all agents survived.
- `0.0` means all agents died.
- `0.668` means around 66.8% of agents survived.

---

## Total Deaths

**Definition:**  
The total number of agents that died during the simulation.

```text
total_dead = initial_population - final_alive
```

**Interpretation:**  
A higher total death count indicates stronger system failure or poor adaptation to scarcity.

**Why it matters:**  
This metric complements survival rate by showing the absolute number of failed agents.

---

## Final Alive Agents

**Definition:**  
The number of agents alive at the final timestep.

**Interpretation:**  
This metric gives a direct population-level outcome at the end of a run.

**Why it matters:**  
It is useful for comparing runs with the same initial population size.

---

## Final Price

**Definition:**  
The food price at the final timestep.

**Interpretation:**  
A high final price suggests that food remained scarce or that the economy ended under pressure.

**Why it matters:**  
Final price captures the ending condition of the market.

---

## Average Price

**Definition:**  
The average food price across all timesteps.

```text
avg_price = mean(food_price over time)
```

**Interpretation:**  
A higher average price means agents experienced stronger resource pressure during the simulation.

**Why it matters:**  
Average price is a proxy for long-term scarcity pressure.

---

## Price Volatility

**Definition:**  
The standard deviation of food price across timesteps.

```text
price_volatility = std(food_price over time)
```

**Interpretation:**  
A high value means that the food market was unstable.

**Why it matters:**  
Even if agents survive, high volatility indicates an unstable environment.

---

## Gini Survivor

**Definition:**  
The Gini coefficient calculated only among surviving agents.

**Interpretation:**  
This measures inequality among agents that are still alive.

**Why it matters:**  
It shows whether surviving agents end up with similar or unequal wealth levels.

**Important note:**  
This metric ignores dead agents. Therefore, it may understate system-wide inequality when many agents die.

---

## Gini Population

**Definition:**  
The Gini coefficient calculated over the initial population, treating dead agents as having zero wealth.

**Interpretation:**  
This metric captures both inequality and the effect of death.

**Why it matters:**  
It better reflects population-level welfare loss than `gini_survivor`.

**Example interpretation:**  
If many agents die, `gini_population` can become much higher than `gini_survivor`.

---

## Gather Count

**Definition:**  
The number of agents choosing the `gather` action at a timestep.

**Action meaning:**  
`gather` means the agent produces food.

**Interpretation:**  
A higher gather count means more agents are focusing on direct food production.

**Why it matters:**  
Under scarcity, adaptive policies are expected to increase gather behavior.

---

## Work Count

**Definition:**  
The number of agents choosing the `work` action at a timestep.

**Action meaning:**  
`work` means the agent produces coin.

**Interpretation:**  
A higher work count means more agents are focusing on earning money rather than producing food.

**Why it matters:**  
Work can be useful when food is available through trade, but it can become risky under severe scarcity.

---

## Gather Ratio

**Definition:**  
The proportion of total actions that are `gather`.

```text
gather_ratio = total_gather_actions / total_actions
```

**Interpretation:**  
A higher gather ratio means agents are more food-production oriented.

**Why it matters:**  
This is a key behavioral adaptation metric. In scarcity scenarios, a stronger policy should generally increase gather behavior.

---

## Work Ratio

**Definition:**  
The proportion of total actions that are `work`.

```text
work_ratio = total_work_actions / total_actions
```

**Interpretation:**  
A higher work ratio means agents are more coin-production oriented.

**Why it matters:**  
This metric helps explain whether agents prioritize money or direct survival resources.

---

## Average Trades

**Definition:**  
The average number of trades per timestep.

```text
avg_trades = mean(trades over time)
```

**Interpretation:**  
A higher value means agents rely more on the market to survive.

**Why it matters:**  
Trade activity can indicate market dependency or food shortage. In stressed environments, high trade activity may reflect survival pressure.

---

## Total Deaths From Steps

**Definition:**  
The sum of deaths recorded at each timestep.

```text
total_deaths_from_steps = sum(deaths_this_step)
```

**Interpretation:**  
This should match the final total death count.

**Why it matters:**  
It is useful as a consistency check for simulation logs.

---

# Scenario Definitions

The simulation is evaluated under multiple environmental scenarios.

## Default Scenario

The default scenario represents a low-stress environment.

**Configuration:**

```python
"default": None
```

This uses the default world configuration.

**Expected behavior:**

- Most or all agents survive.
- Random and rule-based policies may perform similarly.
- The environment may not be difficult enough to expose strong policy differences.

---

## Moderate Scarcity Scenario

The moderate scarcity scenario introduces resource pressure without immediately causing total collapse.

**Configuration:**

```python
"moderate_scarcity": {
    "base_gain": 2.2,
    "ideal_food_per_agent": 6.5,
    "trade_limit_ratio": 0.4,
}
```

**Expected behavior:**

- Random agents may partially survive but experience economic pressure.
- Rule-based agents are expected to adapt better.
- This scenario is useful for observing welfare loss before total collapse.

**Why it matters:**  
This scenario captures the difference between merely surviving and maintaining a stable economy.

---

## Scarcity Scenario

The scarcity scenario represents a high-stress environment.

**Configuration:**

```python
"scarcity": {
    "base_gain": 1.7,
    "ideal_food_per_agent": 7.0,
    "trade_limit_ratio": 0.3,
}
```

**Expected behavior:**

- Random agents are likely to collapse.
- Adaptive policies should increase food production behavior.
- Strong differences between policies should become visible.

---

# Interpretation Strategy

The metrics should be interpreted together rather than independently.

For example:

- High survival rate with high Gini may indicate survival with inequality.
- Low death count with high price volatility may indicate unstable survival.
- High gather ratio under scarcity may indicate adaptive behavior.
- High average trades may indicate market dependency.
- Low survival rate with high final price indicates system collapse under scarcity.

The most important comparison in Chapter 1 is between:

```text
random policy vs rule-based policy
```

across:

```text
default
moderate_scarcity
scarcity
```

This establishes a non-LLM baseline before any advanced decision-making policy is introduced.
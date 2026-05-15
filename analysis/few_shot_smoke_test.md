# Few-Shot LLM Smoke Test Results

This document records the first smoke test for the few-shot LLM policies.

This is not a final experiment result. The purpose of this test is to verify that the few-shot LLM policies run correctly inside the simulation loop and produce valid `gather` / `work` actions.

---

## Test Setup

| Setting | Value |
|---|---|
| Model | `qwen3:8b` via Ollama |
| Prompting method | Few-shot objective prompting |
| Scenario | `moderate_scarcity` |
| Agents | 5 |
| Timesteps | 10 |
| Seed | 1 |
| Policies | `llm_survival_few_shot`, `llm_social_welfare_few_shot`, `llm_wealth_maximizing_few_shot` |

The test uses the same small smoke-test configuration as the zero-shot smoke test so that early behavior patterns can be compared.

---

## Results

| Policy | Alive | Dead Total | Final Price | Total Gather | Total Work | Gather Ratio | Work Ratio | Final Gini Population |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `llm_survival_few_shot` | 5 | 0 | 3.9009 | 28 | 22 | 0.56 | 0.44 | 0.0557 |
| `llm_social_welfare_few_shot` | 5 | 0 | 2.0171 | 40 | 10 | 0.80 | 0.20 | 0.0501 |
| `llm_wealth_maximizing_few_shot` | 5 | 0 | 7.4223 | 20 | 30 | 0.40 | 0.60 | 0.0699 |

---

## Interpretation

The few-shot smoke test confirms that the few-shot LLM policies are correctly connected to the simulation and return valid simulator actions.

Compared with the earlier zero-shot smoke test, the few-shot policies produced less extreme behavior:

- `llm_survival_few_shot` produced a balanced gather/work distribution.
- `llm_social_welfare_few_shot` still favored gathering, but it did not choose gather 100% of the time.
- `llm_wealth_maximizing_few_shot` still favored work, but it also gathered enough food to keep all agents alive in this small test.

This is an important early signal because the zero-shot wealth-maximizing policy previously over-prioritized work and caused collapse.

---

## Comparison With Zero-Shot Smoke Test

| Objective | Zero-Shot Behavior | Few-Shot Behavior |
|---|---|---|
| Survival | Mixed behavior, but less guided | More balanced gather/work behavior |
| Social welfare | Strongly gather-focused, 100% gather | Still gather-focused, but allows some work |
| Wealth maximizing | Over-prioritized work and collapsed | Still work-focused, but includes survival guardrail |

The few-shot examples appear to guide the LLM away from extreme zero-shot behavior while preserving the intended objective differences.

---

## Key Observation

The few-shot setup did not simply make every policy identical.

The policies still show different behavior patterns:

- Survival: balanced
- Social welfare: gather-heavy
- Wealth maximizing: work-heavy, but not suicidal

This supports the idea that few-shot prompting can make LLM agents more controllable without removing policy diversity.

---

## Limitations

This is only a smoke test.

The results should not be treated as final experimental evidence because the run is small:

- only 5 agents
- only 10 timesteps
- only 1 seed
- only the `moderate_scarcity` scenario

The purpose is to validate the few-shot integration and check whether the first behavior signal is reasonable.

---

## Next Step

The next step is to run a small few-shot comparison experiment under the same conditions as the zero-shot small experiment:

| Setting | Value |
|---|---|
| Agents | 10 |
| Timesteps | 30 |
| Seed | 1 |
| Scenarios | `default`, `moderate_scarcity`, `scarcity` |
| Policies | baseline + zero-shot + few-shot |

After that, few-shot results can be compared against zero-shot and rule-based baselines using the same summary and graph pipeline.
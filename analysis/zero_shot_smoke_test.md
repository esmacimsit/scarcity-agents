# Zero-Shot LLM Smoke Test Results

This document records the first small smoke test for the zero-shot LLM policies.

This is not a final experiment result. The goal of this test is only to verify that the zero-shot LLM policies can run inside the simulation loop and produce valid actions.

---

## Test Setup

| Setting | Value |
|---|---|
| Model | `qwen3:8b` via Ollama |
| Scenario | `moderate_scarcity` |
| Agents | 5 |
| Timesteps | 10 |
| Seed | 1 |
| Policies | `llm_survival`, `llm_social_welfare`, `llm_wealth_maximizing` |

The test uses a very small configuration to quickly check runtime behavior before running larger zero-shot experiments.

---

## Results

| Policy | Alive | Dead Total | Final Price | Total Gather | Total Work | Gather Ratio | Work Ratio | Final Gini Population |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `llm_survival` | 5 | 0 | 3.6236 | 24 | 26 | 0.48 | 0.52 | 0.0773 |
| `llm_social_welfare` | 5 | 0 | 1.2959 | 50 | 0 | 1.00 | 0.00 | 0.0481 |
| `llm_wealth_maximizing` | 0 | 5 | 10.0000 | 0 | 20 | 0.00 | 1.00 | 0.0000 |

---

## Interpretation

The smoke test confirms that the zero-shot LLM policies are connected to the simulation and return valid simulator actions.

The three objectives produced clearly different behavior patterns:

- `llm_survival` produced a mixed gather/work distribution.
- `llm_social_welfare` strongly favored gathering, which kept all agents alive and reduced the food price.
- `llm_wealth_maximizing` strongly favored working, which caused food production to collapse and all agents to die in this small stress test.

This supports the main Chapter 2 direction:

> The same local LLM can produce different society-level outcomes when controlled by different decision objectives.

---

## Limitations

This is only a smoke test.

The results should not be treated as final experimental evidence because the run is small:

- only 5 agents
- only 10 timesteps
- only 1 seed
- only the `moderate_scarcity` scenario

The purpose is to validate the integration and observe early behavior signals.

---

## Next Step

The next step is to run a slightly larger zero-shot experiment and save its results through the normal CSV/logging pipeline.

After that, the zero-shot results can be compared against the existing `random` and `rule` baselines using the same summary and graph scripts.
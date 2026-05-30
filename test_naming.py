#!/usr/bin/env python
"""Test the naming logic for zero-shot files"""

from pathlib import Path

zero_shot_dir = Path(r"c:\Users\Lenovo\Desktop\ai_society\logs_to_read\zero_shot_small_experiment")

print("Testing zero-shot file naming:")
print("=" * 60)

for file in sorted(zero_shot_dir.glob("*_step_log.csv")):
    scenario_name = file.name.replace("_step_log.csv", "")
    
    # Test the naming logic
    parts = scenario_name.rsplit("_seed_", 1)
    if len(parts) == 2:
        unique_key = f"{parts[0]}_zero_shot_seed_{parts[1]}"
    else:
        unique_key = scenario_name
    
    print(f"Original:   {scenario_name}")
    print(f"Transformed: {unique_key}")
    print()

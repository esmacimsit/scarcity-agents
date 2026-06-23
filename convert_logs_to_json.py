"""
Data processing script to convert CSV logs to JSON format for the frontend.
Reads simulation logs from CSV files and converts them to the format expected by the visualization.
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

# Paths
LOGS_DIR = Path(r"C:\Users\Lenovo\Desktop\log")
LOGS_TO_READ_DIR = Path(r"C:\Users\Lenovo\Desktop\log")
OUTPUT_DIR = Path(r"C:\Users\Lenovo\Desktop\bu\scarcity-agents\frontend\public\logs")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_available_experiments() -> Dict[str, Dict[str, Path]]:
    """
    Scan logs and logs_to_read directories to find all available experiments.
    Returns a dictionary mapping scenario names to their log file paths.
    """
    experiments = {}
    
    # Scan logs directory for standalone CSV files
    if LOGS_DIR.exists():
        for file in LOGS_DIR.glob("*_step_log.csv"):
            # Extract scenario name from filename
            # e.g., "default_llm_social_welfare_seed_1_step_log.csv" -> "default_llm_social_welfare_seed_1"
            scenario_name = file.name.replace("_step_log.csv", "")
            agent_log_file = LOGS_DIR / f"{scenario_name}_agent_log.csv"
            
            experiments[scenario_name] = {
                "step_log": file,
                "agent_log": agent_log_file if agent_log_file.exists() else None
            }
    
    # Scan logs_to_read subdirectories
    if LOGS_TO_READ_DIR.exists():
        for subdir in LOGS_TO_READ_DIR.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*_step_log.csv"):
                    scenario_name = file.name.replace("_step_log.csv", "")
                    agent_log_file = subdir / f"{scenario_name}_agent_log.csv"
                    
                    # If agent_log not in subdirectory, look in main logs directory
                    if not agent_log_file.exists():
                        agent_log_file = LOGS_DIR / f"{scenario_name}_agent_log.csv"
                    
                    # Only proceed if we found either the step_log or if step_log exists (try without agent)
                    if file.exists():
                        # Extract method from directory name
                        dir_name = subdir.name.lower()
                        
                        # Build unique key with method prefix if not already in name
                        # Only add few_shot/zero_shot prefix to LLM scenarios
                        if "few_shot" in dir_name and "few_shot" not in scenario_name and "llm" in scenario_name:
                            # Add few_shot prefix: default_llm_social_welfare_seed_1 -> default_llm_social_welfare_few_shot_seed_1
                            parts = scenario_name.rsplit("_seed_", 1)
                            unique_key = f"{parts[0]}_few_shot_seed_{parts[1]}" if len(parts) == 2 else scenario_name
                        elif "zero_shot" in dir_name and "zero_shot" not in scenario_name and "llm" in scenario_name:
                            # Add zero_shot prefix
                            parts = scenario_name.rsplit("_seed_", 1)
                            unique_key = f"{parts[0]}_zero_shot_seed_{parts[1]}" if len(parts) == 2 else scenario_name
                        elif "finetuned" in dir_name and "finetuned" not in scenario_name:
                            # Add finetuned prefix
                            parts = scenario_name.rsplit("_seed_", 1)
                            unique_key = f"{parts[0]}_finetuned_seed_{parts[1]}" if len(parts) == 2 else scenario_name
                        else:
                            # Name already has the method or no matching directory or not LLM
                            unique_key = scenario_name
                        
                        experiments[unique_key] = {
                            "step_log": file,
                            "agent_log": agent_log_file if agent_log_file and agent_log_file.exists() else None
                        }
    
    return experiments


def convert_csv_to_json(step_log_path: Path, agent_log_path, output_name: str) -> bool:
    """
    Convert CSV log files to JSON format for the frontend.
    
    Args:
        step_log_path: Path to step_log CSV file
        agent_log_path: Path to agent_log CSV file (can be None)
        output_name: Name for the output JSON file (without .json extension)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read CSV files
        print(f"  Reading {step_log_path.name}...")
        step_df = pd.read_csv(step_log_path)
        
        # Read agent log if it exists
        if agent_log_path and agent_log_path.exists():
            print(f"  Reading {agent_log_path.name}...")
            agent_df = pd.read_csv(agent_log_path)
        else:
            print(f"  Agent log not found, using empty DataFrame...")
            agent_df = pd.DataFrame()  # Empty DataFrame for agent data
        
        # Extract policy from step_log
        policy = step_df['policy'].iloc[0] if len(step_df) > 0 else "unknown"
        
        # Convert step_log to list of dictionaries
        step_log = step_df.to_dict('records')
        
        # Convert agent_log to list of dictionaries
        agent_log = agent_df.to_dict('records')
        
        # Create output JSON structure
        output_data = {
            "metadata": {
                "policy": policy,
                "source_files": {
                    "step_log": step_log_path.name,
                    "agent_log": agent_log_path.name if agent_log_path else "not available"
                }
            },
            "step_log": step_log,
            "agent_log": agent_log
        }
        
        # Write to JSON file
        output_path = OUTPUT_DIR / f"{output_name}.json"
        print(f"  Writing {output_path.name}...")
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"  ✓ Successfully converted to {output_name}.json")
        print(f"    - Step records: {len(step_log)}")
        print(f"    - Agent records: {len(agent_log)}")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error converting {output_name}: {e}")
        return False


def create_scenario_manifest() -> None:
    """
    Create a manifest file listing all available scenarios for the frontend.
    """
    try:
        experiments = get_available_experiments()
        
        manifest = {
            "available_scenarios": list(experiments.keys()),
            "total_scenarios": len(experiments),
            "experiment_groups": {}
        }
        
        # Group scenarios by scarcity level and type
        for scenario in experiments.keys():
            # Determine scarcity level
            if "moderate_scarcity" in scenario:
                scarcity = "moderate_scarcity"
            elif "default" in scenario or scenario.startswith("default_"):
                scarcity = "default"
            else:
                scarcity = "high_scarcity"
            
            # Determine experiment type
            if "finetuned" in scenario:
                exp_type = "fine-tuned"
            elif "few_shot" in scenario:
                exp_type = "few-shot"
            elif "random" in scenario:
                exp_type = "random"
            elif "rule" in scenario:
                exp_type = "rule-based"
            elif "llm" in scenario:
                exp_type = "llm" 
            else:
                exp_type = "baseline"
            
            # Create group key
            if "social_welfare" in scenario:
                policy = "social_welfare"
            elif "survival" in scenario:
                policy = "survival"
            elif "wealth_maximizing" in scenario:
                policy = "wealth_maximizing"
            elif "random" in scenario:
                policy = "random"
            elif "rule" in scenario:
                policy = "rule"
            else:
                policy = "baseline"
            
            group_key = f"{scarcity}_{exp_type}_{policy}"
            
            if group_key not in manifest["experiment_groups"]:
                manifest["experiment_groups"][group_key] = []
            manifest["experiment_groups"][group_key].append(scenario)
        
        manifest_path = OUTPUT_DIR / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✓ Created scenario manifest with {len(experiments)} scenarios")
        print(f"  Groups found: {len(manifest['experiment_groups'])}")
    except Exception as e:
        print(f"✗ Error creating manifest: {e}")


def main():
    """Main conversion function."""
    print("\n" + "="*60)
    print("CSV to JSON Data Conversion for Scarcity Agents Frontend")
    print("="*60)
    
    # Get all available experiments
    print("\nScanning for experiments...")
    experiments = get_available_experiments()
    
    if not experiments:
        print("✗ No experiments found in logs directories")
        return
    
    print(f"✓ Found {len(experiments)} experiments\n")
    
    # Convert each experiment
    successful = 0
    failed = 0
    
    for scenario_name, log_files in experiments.items():
        print(f"Converting: {scenario_name}")
        if convert_csv_to_json(
            log_files["step_log"],
            log_files["agent_log"],
            scenario_name
        ):
            successful += 1
        else:
            failed += 1
    
    # Create manifest
    create_scenario_manifest()
    
    # Summary
    print("\n" + "="*60)
    print(f"Conversion Complete: {successful} successful, {failed} failed")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()




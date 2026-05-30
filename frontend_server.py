"""
Simple HTTP server to serve simulation data and handle dynamic log conversions.
Can be run locally to watch for new CSV logs and convert them to JSON on-the-fly.
"""

import os
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from datetime import datetime
import pandas as pd

# Configuration
LOGS_DIR = Path(r"c:\Users\Lenovo\Desktop\ai_society\logs")
LOGS_TO_READ_DIR = Path(r"c:\Users\Lenovo\Desktop\ai_society\logs_to_read")
OUTPUT_DIR = Path(r"c:\Users\Lenovo\Desktop\bitirme projesi\scarcity-agents\frontend\public\logs")
FRONTEND_PORT = 5173  # Vite default dev server port


class LogConversionServer(SimpleHTTPRequestHandler):
    """HTTP handler that serves logs and handles conversions."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/api/refresh':
            # Endpoint to trigger a refresh of all logs
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            result = refresh_all_logs()
            self.wfile.write(json.dumps(result).encode())
            
        elif self.path == '/api/new-logs':
            # Endpoint to check for and convert new logs
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            new_count = check_and_convert_new_logs()
            self.wfile.write(json.dumps({
                "new_logs_converted": new_count,
                "timestamp": datetime.now().isoformat()
            }).encode())
        else:
            super().do_GET()


def convert_csv_to_json(step_log_path: Path, agent_log_path: Path, output_name: str) -> bool:
    """Convert CSV log files to JSON format."""
    try:
        step_df = pd.read_csv(step_log_path)
        agent_df = pd.read_csv(agent_log_path)
        
        policy = step_df['policy'].iloc[0] if len(step_df) > 0 else "unknown"
        
        output_data = {
            "metadata": {
                "policy": policy,
                "source_files": {
                    "step_log": step_log_path.name,
                    "agent_log": agent_log_path.name
                }
            },
            "step_log": step_df.to_dict('records'),
            "agent_log": agent_df.to_dict('records')
        }
        
        output_path = OUTPUT_DIR / f"{output_name}.json"
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error converting {output_name}: {e}")
        return False


def check_and_convert_new_logs() -> int:
    """Check for new CSV logs and convert them."""
    converted_count = 0
    
    # Get existing JSON files
    existing_jsons = {f.stem for f in OUTPUT_DIR.glob("*.json")}
    
    # Check logs directory
    if LOGS_DIR.exists():
        for file in LOGS_DIR.glob("*_step_log.csv"):
            scenario_name = file.name.replace("_step_log.csv", "")
            
            if scenario_name not in existing_jsons:
                agent_log_file = LOGS_DIR / f"{scenario_name}_agent_log.csv"
                if agent_log_file.exists():
                    if convert_csv_to_json(file, agent_log_file, scenario_name):
                        print(f"✓ Converted new log: {scenario_name}")
                        converted_count += 1
    
    # Check logs_to_read subdirectories
    if LOGS_TO_READ_DIR.exists():
        for subdir in LOGS_TO_READ_DIR.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*_step_log.csv"):
                    scenario_name = file.name.replace("_step_log.csv", "")
                    unique_key = f"{subdir.name}_{scenario_name}"
                    
                    if unique_key not in existing_jsons:
                        agent_log_file = subdir / f"{scenario_name}_agent_log.csv"
                        if agent_log_file.exists():
                            if convert_csv_to_json(file, agent_log_file, unique_key):
                                print(f"✓ Converted new log: {unique_key}")
                                converted_count += 1
    
    return converted_count


def refresh_all_logs() -> dict:
    """Re-convert all logs from scratch."""
    print("Refreshing all logs...")
    converted = 0
    skipped = 0
    
    if LOGS_DIR.exists():
        for file in LOGS_DIR.glob("*_step_log.csv"):
            scenario_name = file.name.replace("_step_log.csv", "")
            agent_log_file = LOGS_DIR / f"{scenario_name}_agent_log.csv"
            if agent_log_file.exists():
                if convert_csv_to_json(file, agent_log_file, scenario_name):
                    converted += 1
                else:
                    skipped += 1
    
    if LOGS_TO_READ_DIR.exists():
        for subdir in LOGS_TO_READ_DIR.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*_step_log.csv"):
                    scenario_name = file.name.replace("_step_log.csv", "")
                    unique_key = f"{subdir.name}_{scenario_name}"
                    agent_log_file = subdir / f"{scenario_name}_agent_log.csv"
                    if agent_log_file.exists():
                        if convert_csv_to_json(file, agent_log_file, unique_key):
                            converted += 1
                        else:
                            skipped += 1
    
    return {
        "converted": converted,
        "skipped": skipped,
        "timestamp": datetime.now().isoformat()
    }


def monitor_logs_periodic():
    """Periodically check for new logs (runs in background thread)."""
    while True:
        time.sleep(60)  # Check every 60 seconds
        new_count = check_and_convert_new_logs()
        if new_count > 0:
            print(f"[{datetime.now().isoformat()}] Found and converted {new_count} new logs")


def main():
    """Main server function."""
    print("\n" + "="*60)
    print("Scarcity Agents Log Server")
    print("="*60)
    print(f"Logs directory: {LOGS_DIR.resolve()}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    print(f"Starting monitor thread...")
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_logs_periodic, daemon=True)
    monitor_thread.start()
    
    print(f"Starting HTTP server on http://localhost:{FRONTEND_PORT}")
    print("Press Ctrl+C to stop\n")
    
    try:
        server = HTTPServer(('localhost', FRONTEND_PORT), LogConversionServer)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()

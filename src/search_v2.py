import os
import json
import sys

def main():
    # Reconfigure stdout/stderr to use UTF-8 and handle errors gracefully
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    print("=== SEARCHING WORKSPACE FOR FILES CONTAINING 'v2', 'warm_start', or 'champion_v2' ===")
    matches = []
    for root, dirs, files in os.walk("."):
        # Skip standard venv or .git directories to keep things clean and avoid searching massive external packages
        if any(ignored in root for ignored in [".venv", ".git"]):
            continue
        for file in files:
            lower_name = file.lower()
            if "v2" in lower_name or "warm_start" in lower_name or "champion_v2" in lower_name:
                full_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(full_path)
                except Exception as e:
                    size = f"Error reading size: {e}"
                matches.append((full_path, size))
    
    if matches:
        for path, size in sorted(matches, key=lambda x: x[0]):
            print(f"Found: {path} (Size: {size} bytes)")
    else:
        print("No matching files found in the workspace.")

    print("\n=== SCANNING 'archive/iter_220/results/' FOR ANY FILES ===")
    results_dir = "archive/iter_220/results/"
    if os.path.exists(results_dir):
        try:
            results_files = os.listdir(results_dir)
            if results_files:
                for file in sorted(results_files):
                    full_path = os.path.join(results_dir, file)
                    if os.path.isfile(full_path):
                        try:
                            size = os.path.getsize(full_path)
                        except Exception as e:
                            size = f"Error: {e}"
                        print(f"File: {file} (Size: {size} bytes)")
            else:
                print("The folder is empty.")
        except Exception as e:
            print(f"Error listing 'archive/iter_220/results/': {e}")
    else:
        print("Directory 'archive/iter_220/results/' does not exist.")

    print("\n=== PRINTING CONTENT/SUMMARY OF TARGET/NEWLY CREATED FILES ===")
    # Target files specifically mentioned: 'archive/iter_220/results/champion_v2_rule.json'
    target_files = ["archive/iter_220/results/champion_v2_rule.json"]
    # Also include any newly found matching files in matches list
    for path, size in matches:
        if path not in target_files:
            target_files.append(path)

    for path in target_files:
        if os.path.exists(path) and os.path.isfile(path):
            print(f"\n--- Content of {path} (Size: {os.path.getsize(path)} bytes) ---")
            # If it's a very large binary file, we might not want to print it raw
            if path.endswith((".gif", ".png", ".jpg", ".jpeg", ".pyc")):
                print("[Binary/Image file - skipping raw content print]")
            else:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if path.endswith(".json"):
                        try:
                            # Try pretty printing JSON
                            parsed = json.loads(content)
                            print(json.dumps(parsed, indent=2))
                        except Exception:
                            print(content)
                    else:
                        # Print up to 100 lines for other files as summary
                        lines = content.splitlines()
                        if len(lines) > 100:
                            print("\n".join(lines[:100]))
                            print(f"... [Truncated. Total lines: {len(lines)}]")
                        else:
                            print(content)
                except Exception as e:
                    print(f"Error reading content of {path}: {e}")
        else:
            if path == "archive/iter_220/results/champion_v2_rule.json":
                print(f"Target file '{path}' does not exist.")

if __name__ == "__main__":
    main()

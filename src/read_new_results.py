import os

json_candidates = ["archive/iter_220/results/champion_v2_rule.json", "archive/iter_220/results/champion_rule.json"]
csv_candidates = ["archive/iter_220/results/evolution_summary_v2.csv", "archive/iter_220/results/evolution_summary.csv"]

json_file = None
for candidate in json_candidates:
    if os.path.exists(candidate):
        json_file = candidate
        break

csv_file = None
for candidate in csv_candidates:
    if os.path.exists(candidate):
        csv_file = candidate
        break

# Check and read JSON file
if json_file:
    print(f"=== {json_file} ===")
    with open(json_file, "r", encoding="utf-8") as f:
        content = f.read()
    print(content)
    print()
else:
    print("No champion rule JSON file found.")
    print()

# Check and read CSV file
if csv_file:
    print(f"=== {csv_file} ===")
    with open(csv_file, "r", encoding="utf-8") as f:
        content = f.read()
    print(content)
    print()
else:
    print("No evolution summary CSV file found.")
    print()

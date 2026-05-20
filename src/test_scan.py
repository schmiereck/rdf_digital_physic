import json
import os
from pathlib import Path

def extract_rules_from_json(data):
    rules = []
    if isinstance(data, dict):
        if "rule_dict" in data:
            rules.append(data["rule_dict"])
        for k, v in data.items():
            if k in ["population", "warm_start_population"] and isinstance(v, list):
                for item in v:
                    rules.extend(extract_rules_from_json(item))
            elif isinstance(v, (dict, list)):
                rules.extend(extract_rules_from_json(v))
    elif isinstance(data, list):
        for item in data:
            rules.extend(extract_rules_from_json(item))
    return rules

def standardize_rule(rule_dict: dict) -> tuple:
    return tuple(int(rule_dict.get(str(i), rule_dict.get(i, i))) for i in range(128))

def main():
    target_iters = ["iter_215", "iter_218", "iter_221", "iter_222"]
    archive_dir = Path("archive")
    
    all_json_files = []
    for iter_name in target_iters:
        results_dir = archive_dir / iter_name / "results"
        if results_dir.exists():
            for f in results_dir.glob("*.json"):
                all_json_files.append(f)
                
    print(f"Found {len(all_json_files)} JSON files in target directories:")
    for f in all_json_files:
        print(f"  {f}")
        
    unique_rules = {}
    for f in all_json_files:
        try:
            with open(f) as fh:
                data = json.load(fh)
            extracted = extract_rules_from_json(data)
            print(f"  Extracted {len(extracted)} rules from {f}")
            for r in extracted:
                std = standardize_rule(r)
                if std not in unique_rules:
                    unique_rules[std] = set()
                unique_rules[std].add(str(f))
        except Exception as e:
            print(f"  Error reading {f}: {e}")
            
    print(f"Total unique rules: {len(unique_rules)}")

if __name__ == "__main__":
    main()

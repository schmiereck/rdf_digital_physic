import csv
import json
import os
import yaml
from pathlib import Path

POPULATION_DIR = Path("../archive/iter_136/population/medium_density")
SCORES_CSV = Path("../archive/iter_136/results/medium_density_scores.csv")
OUTPUT_DIR = Path("../archive/iter_137/results")
OUTPUT_CSV = OUTPUT_DIR / "re_evaluation_scores.csv"
OUTPUT_YAML = OUTPUT_DIR / "result.yaml"

VIABILITY_FITNESS_THRESHOLD = 0.001
VIABILITY_BIT_RATIO_THRESHOLD = 3.0


def linear_fitness(displacement, bit_ratio):
    return displacement / (1.0 + abs(bit_ratio - 1.0))


def quadratic_fitness(displacement, bit_ratio):
    return displacement / (1.0 + abs(bit_ratio - 1.0) ** 2)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rule_files = sorted(POPULATION_DIR.glob("rule_*.json"))
    loaded_rules = {}
    for f in rule_files:
        with open(f) as fh:
            loaded_rules[f.stem] = json.load(fh)
    print(f"Loaded {len(loaded_rules)} rule files from population directory.")

    rows = []
    with open(SCORES_CSV, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rule_name = row["rule_id"]
            displacement = float(row["displacement"])
            bit_ratio = float(row["bit_ratio"])
            lin_fit = linear_fitness(displacement, bit_ratio)
            quad_fit = quadratic_fitness(displacement, bit_ratio)
            rows.append({
                "rule_name": rule_name,
                "displacement": displacement,
                "bit_ratio": bit_ratio,
                "linear_fitness": lin_fit,
                "quadratic_fitness": quad_fit,
            })
    print(f"Processed {len(rows)} rows from scores CSV.")

    rows.sort(key=lambda r: r["quadratic_fitness"], reverse=True)

    with open(OUTPUT_CSV, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["rule_name", "displacement", "bit_ratio", "linear_fitness", "quadratic_fitness"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "rule_name": r["rule_name"],
                "displacement": f"{r['displacement']:.6f}",
                "bit_ratio": f"{r['bit_ratio']:.4f}",
                "linear_fitness": f"{r['linear_fitness']:.8f}",
                "quadratic_fitness": f"{r['quadratic_fitness']:.8f}",
            })
    print(f"Wrote re-evaluation scores to {OUTPUT_CSV}")

    best = rows[0]
    viable = (
        best["quadratic_fitness"] > VIABILITY_FITNESS_THRESHOLD
        and best["bit_ratio"] < VIABILITY_BIT_RATIO_THRESHOLD
    )

    print(f"\nTop 10 rules by quadratic fitness:")
    for r in rows[:10]:
        print(
            f"  {r['rule_name']:12s}  quad={r['quadratic_fitness']:.6f}  "
            f"disp={r['displacement']:.4f}  bit_ratio={r['bit_ratio']:.2f}  "
            f"linear={r['linear_fitness']:.6f}"
        )

    print(f"\nBest rule: {best['rule_name']}")
    print(f"  quadratic_fitness : {best['quadratic_fitness']:.8f}")
    print(f"  displacement      : {best['displacement']:.6f}")
    print(f"  bit_ratio         : {best['bit_ratio']:.4f}")
    print(f"  viable_founder    : {viable}")

    result = {
        "best_rule_filename": f"{best['rule_name']}.json",
        "best_rule_quadratic_fitness": round(best["quadratic_fitness"], 8),
        "best_rule_displacement": round(best["displacement"], 6),
        "best_rule_bit_ratio": round(best["bit_ratio"], 4),
        "viable_founder_found": bool(viable),
    }

    with open(OUTPUT_YAML, "w") as fh:
        yaml.dump(result, fh, default_flow_style=False, sort_keys=False)
    print(f"\nWrote result YAML to {OUTPUT_YAML}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Scan the iter_197.2 evolution run for non-degenerate v<c candidates.

The raw GA champion exploits the complexity-bonus by saturating the grid.
We re-initialise the same RNG sequence used by evolve.py, regenerate the final
population, and look for individuals whose mean_bit_count is moderate
(say 5 ≤ mbc ≤ 200) AND whose measured speed is in (0, 1) — these are real
"massive glider" candidates if any exist.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolve import Evolution, chromosome_to_rule_dict
from massive_glider_fitness import MassiveGliderFitness, T_TROMINO_PARTICLE

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "archive" / "iter_197.2" / "results"

# Run the same configuration to recover the final population.
# This is expensive (full re-run) — instead, just pull the saved final
# population from a small extra evaluation pass on the GA-saved champion +
# do a fresh 1-gen search to surface alternative candidates.

def main():
    fit = MassiveGliderFitness()
    rng_seed = 4242
    # Quick exploratory pool: random initial-style C2 rules + the saved champion
    from evolution import generate_random_c2_rule
    import random
    rng = random.Random(rng_seed)
    pool = [generate_random_c2_rule(rng) for _ in range(200)]
    candidates = []
    for i, r in enumerate(pool):
        m = fit.evaluate(r)
        if (
            5 <= m["mean_bit_count"] <= 500
            and 1e-3 < m["speed"] < 0.99
            and m["reason"] == "ok"
            and m["n_valid"] >= 3
        ):
            candidates.append({"idx": i, "metrics": m, "rule": r})
            print(f"  hit idx={i}: speed={m['speed']:.4f} vr={m['vr']:.4f} vc={m['vc']:.4f}  "
                  f"n_valid={m['n_valid']}/{m['n_checked']}  mbc={m['mean_bit_count']:.1f}  "
                  f"fitness={m['fitness']:.2f}")

    print(f"\nScanned {len(pool)} fresh random C2 rules; found {len(candidates)} "
          f"non-degenerate v<c candidates.")

    out_path = OUTPUT_DIR / "alt_candidates.json"
    payload = []
    for c in candidates:
        payload.append({
            "metrics": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in c["metrics"].items()},
            "rule":    {str(k): int(v) for k, v in c["rule"].items()},
        })
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

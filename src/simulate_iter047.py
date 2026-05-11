#!/usr/bin/env python3
"""
iter_047: Two ADJACENT 3-bit oscillators interact under the rule from iter_044.

Hypothesis: interaction-close — two adjacent 3-bit oscillators, whose active zones
immediately overlap, interact in a non-trivial, bit-conserving manner.

Grid: 100x100 hexagonal, periodic boundaries.
Steps: 200
Kernel: contiguous (A=3, B=6) from find_contiguous_kernel.

Seeds (per task spec):
  Osc1: (21,49), (21,50), (22,50)
  Osc2: (23,49), (23,50), (24,50)
"""

import sys
import yaml
import numpy as np
from pathlib import Path

from find_contiguous_kernel import find_contiguous_kernel
from generate_and_simulate import (
    generate_rule, step_ca, find_ones, centroid, canonical_shape,
    detect_period, get_neighborhood, lsb_to_msb, HEX_DIRS,
)

N = 100
STEPS = 200
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_047" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_047" / "result.yaml"

HEX_DIRS_LOCAL = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


def hex_neighbors(q: int, r: int, n: int = N):
    return [((q + dq) % n, (r + dr) % n) for dq, dr in HEX_DIRS_LOCAL]


def cluster_count(positions: list) -> int:
    if not positions:
        return 0
    pos_set = set(positions)
    visited = set()
    clusters = 0
    for start in positions:
        if start in visited:
            continue
        clusters += 1
        stack = [start]
        while stack:
            p = stack.pop()
            if p in visited:
                continue
            visited.add(p)
            for nb in hex_neighbors(p[0], p[1]):
                if nb in pos_set and nb not in visited:
                    stack.append(nb)
    return clusters


def any_neighbor_in_set(positions_a: set, positions_b: set) -> bool:
    for (q, r) in positions_a:
        for nq, nr in hex_neighbors(q, r):
            if (nq, nr) in positions_b:
                return True
    return False


def make_grid(seed_cells: list) -> np.ndarray:
    grid = np.zeros((N, N), dtype=np.int8)
    for q, r in seed_cells:
        grid[q % N, r % N] = 1
    return grid


def run_simulation(grid: np.ndarray, rule: dict, steps: int):
    positions_history = [find_ones(grid)]
    shapes_history = [canonical_shape(find_ones(grid))]
    bit_counts = [int(grid.sum())]

    for t in range(steps):
        grid = step_ca(grid, rule)
        pos = find_ones(grid)
        cnt = int(grid.sum())
        positions_history.append(pos)
        shapes_history.append(canonical_shape(pos) if pos else frozenset())
        bit_counts.append(cnt)

    return positions_history, shapes_history, bit_counts


def classify_outcome(
    bit_counts: list,
    positions_history: list,
    shapes_history: list,
) -> str:
    if any(c != 6 for c in bit_counts):
        return "CHAOTIC"

    final_pos = positions_history[-1]
    final_count = cluster_count(final_pos)

    if final_count == 0:
        return "ANNIHILATION"

    # Check period
    period = detect_period(shapes_history, start=150, max_period=50)

    if final_count >= 2:
        q_vals = [p[0] for p in final_pos]
        q_spread = max(q_vals) - min(q_vals) if q_vals else 0
        if q_spread > 6:
            return "REFLECTION"
        else:
            return "PASS_THROUGH"
    elif final_count == 1:
        if period > 0:
            return "STABLE_COMPOUND"
        else:
            return "FUSION"
    else:
        if period > 0:
            return "STABLE_COMPOUND"
        return "CHAOTIC"


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    kernel = find_contiguous_kernel()
    if kernel is None:
        print("ERROR: could not find contiguous kernel")
        sys.exit(1)
    A_lsb, B_lsb = kernel
    print(f"Contiguous kernel: A={A_lsb} ('{A_lsb:07b}'), B={B_lsb} ('{B_lsb:07b}')")

    rule = generate_rule(A_lsb, B_lsb)

    # Seeds from task spec — oscillators are adjacent (rows 21-22 and 23-24)
    osc1_seed = [(21, 49), (21, 50), (22, 50)]
    osc2_seed = [(23, 49), (23, 50), (24, 50)]

    initial_bits = len(osc1_seed) + len(osc2_seed)
    print(f"\nInitial total bits: {initial_bits}")
    print(f"Oscillator 1 seed: {osc1_seed}")
    print(f"Oscillator 2 seed: {osc2_seed}")
    assert initial_bits == 6, f"Expected 6 initial bits, got {initial_bits}"

    # Combined simulation
    grid_combined = make_grid(osc1_seed + osc2_seed)
    print(f"\n--- Combined simulation ({STEPS} steps) ---")
    pos_hist, shape_hist, bit_counts = run_simulation(grid_combined, rule, STEPS)

    # Reference single-oscillator simulations (to find interaction step)
    pos_hist_1, _, _ = run_simulation(make_grid(osc1_seed), rule, STEPS)
    pos_hist_2, _, _ = run_simulation(make_grid(osc2_seed), rule, STEPS)

    # Find interaction step: first step (>=1) where combined positions differ
    # from the union of the two independent oscillator simulations.
    # At t=0 both are just the seed placements (no CA update yet), so they match.
    interaction_step = -1
    for t in range(1, STEPS + 1):
        combined_t = set(pos_hist[t])
        union_t = set(pos_hist_1[t]) | set(pos_hist_2[t])
        if combined_t != union_t:
            interaction_step = t
            break

    print(f"\nInteraction step (neighbor/overlap proximity): {interaction_step}")

    # Print step-by-step summary for early steps
    print(f"\nStep-by-step bit counts (first 25 steps):")
    for t in range(0, min(26, STEPS + 1)):
        clusters = cluster_count(pos_hist[t])
        print(f"  t={t:3d}  bits={bit_counts[t]}  clusters={clusters}  pos={pos_hist[t]}")

    print("  ...")
    print(f"\nStep-by-step bit counts (last 25 steps):")
    for t in range(max(0, STEPS - 24), STEPS + 1):
        clusters = cluster_count(pos_hist[t])
        print(f"  t={t:3d}  bits={bit_counts[t]}  clusters={clusters}  pos={pos_hist[t]}")

    # Analysis
    is_bit_conserving = all(c == initial_bits for c in bit_counts)
    print(f"\nis_bit_conserving: {is_bit_conserving}")
    print(f"bit_counts min/max: {min(bit_counts)}/{max(bit_counts)}")

    outcome_class = classify_outcome(bit_counts, pos_hist, shape_hist)
    print(f"outcome_class: {outcome_class}")

    final_pos = pos_hist[-1]
    final_clusters = cluster_count(final_pos)
    period = detect_period(shape_hist, start=150, max_period=50)
    print(f"final clusters: {final_clusters}, oscillation_period: {period}")
    print(f"final positions: {final_pos}")

    if final_clusters == 0:
        final_summary = "All bits annihilated — grid empty."
    elif final_clusters == 1:
        final_summary = (
            f"Single fused cluster of {len(final_pos)} bits"
            + (f", oscillation period {period}." if period > 0 else ", stable or long-period.")
        )
    else:
        final_summary = (
            f"{final_clusters} separate clusters, total {len(final_pos)} bits"
            + (f", oscillation period {period}." if period > 0 else ".")
        )

    # Save per-step data
    steps_data = []
    for t in range(STEPS + 1):
        steps_data.append({
            "step": t,
            "bit_count": int(bit_counts[t]),
            "clusters": int(cluster_count(pos_hist[t])),
            "positions": [list(p) for p in pos_hist[t]],
        })

    with open(RESULTS_DIR / "steps.yaml", "w") as f:
        yaml.dump(steps_data, f, default_flow_style=False)
    print(f"\nWritten: {RESULTS_DIR}/steps.yaml")

    result = {
        "kernel_A_lsb": int(A_lsb),
        "kernel_B_lsb": int(B_lsb),
        "initial_bit_count": initial_bits,
        "is_bit_conserving": bool(is_bit_conserving),
        "interaction_step": int(interaction_step),
        "outcome_class": outcome_class,
        "final_bit_count": int(bit_counts[-1]),
        "final_clusters": int(final_clusters),
        "oscillation_period": int(period),
        "final_state_summary": final_summary,
    }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=True)
    print(f"Written: {RESULT_YAML}")

    print(f"\n=== Summary ===")
    for k, v in result.items():
        print(f"  {k}: {v}")

    return 0 if is_bit_conserving and interaction_step > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

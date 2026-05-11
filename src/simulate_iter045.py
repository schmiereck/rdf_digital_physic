#!/usr/bin/env python3
"""
iter_045: Two 3-bit oscillators interact under the rule from iter_044.

Hypothesis: interaction-oscillator — two 3-bit oscillators, under the rule from iter_044,
interact in a non-trivial, bit-conserving manner.

Grid: 100x100 hexagonal, periodic boundaries.
Steps: 200
Kernel: contiguous (A=3, B=6) from find_contiguous_kernel.
"""

import sys
import yaml
import numpy as np
from pathlib import Path

from find_contiguous_kernel import find_contiguous_kernel
from generate_and_simulate import (
    generate_rule, step_ca, find_ones, centroid, canonical_shape,
    detect_period, get_neighborhood, lsb_to_msb, HEX_DIRS, N as BASE_N
)

N = 100
STEPS = 200
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_045" / "results"
RESULT_YAML = PROJECT_ROOT / "archive" / "iter_045" / "result.yaml"


def hex_neighbors(q: int, r: int, n: int = N):
    """Return the 6 hexagonal neighbors of (q, r) with periodic wrapping."""
    dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
    return [((q + dq) % n, (r + dr) % n) for dq, dr in dirs]


def any_neighbor_in_set(positions_a: set, positions_b: set) -> bool:
    """True if any cell in positions_a is a hex-neighbor of any cell in positions_b."""
    for (q, r) in positions_a:
        for nq, nr in hex_neighbors(q, r):
            if (nq, nr) in positions_b:
                return True
    return False


def cluster_count(positions: list) -> int:
    """Count connected components (hex adjacency) in the given positions."""
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


def classify_outcome(
    bit_counts: list,
    positions_history: list,
    shapes_history: list,
    osc1_ref: list,   # reference single-osc1 positions per step
    osc2_ref: list,   # reference single-osc2 positions per step
    interaction_step: int,
) -> str:
    """Classify the interaction outcome."""
    if any(c != 6 for c in bit_counts):
        return "CHAOTIC"

    final_pos = positions_history[-1]
    final_count = cluster_count(final_pos)
    osc1_final = set(osc1_ref[-1]) if osc1_ref[-1] else set()
    osc2_final = set(osc2_ref[-1]) if osc2_ref[-1] else set()

    # Check if final state matches reference single-oscillator states
    combined_ref = osc1_final | osc2_final
    actual_final = set(final_pos)

    # Check bit conservation
    is_conserving = all(c == 6 for c in bit_counts)

    # Check if two separate clusters at the end
    if final_count >= 2:
        # Check if they're spatially separated like the original
        positions_set = set(final_pos)
        # Are the two groups on different sides of where they started?
        q_vals = [p[0] for p in final_pos]
        q_spread = max(q_vals) - min(q_vals) if q_vals else 0
        # Compare to initial spread of ~4
        if q_spread > 6:
            return "REFLECTION"
        else:
            return "PASS_THROUGH"
    elif final_count == 1:
        # Single connected component
        # Is it stable (period 1 or small period)?
        period = detect_period(shapes_history, start=150, max_period=50)
        if period > 0:
            return "STABLE_COMPOUND"
        else:
            return "FUSION"
    elif final_count == 0:
        return "ANNIHILATION"
    else:
        period = detect_period(shapes_history, start=150, max_period=50)
        if period > 0:
            return "STABLE_COMPOUND"
        return "CHAOTIC"


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


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    kernel = find_contiguous_kernel()
    if kernel is None:
        print("ERROR: could not find contiguous kernel")
        sys.exit(1)
    A_lsb, B_lsb = kernel
    print(f"Contiguous kernel: A={A_lsb} ('{A_lsb:07b}'), B={B_lsb} ('{B_lsb:07b}')")

    rule = generate_rule(A_lsb, B_lsb)

    # --- Oscillator seeds from task spec ---
    osc1_seed = [(21, 49), (21, 50), (22, 50)]
    osc2_seed = [(25, 49), (25, 50), (26, 50)]

    initial_bits = len(osc1_seed) + len(osc2_seed)
    print(f"\nInitial total bits: {initial_bits}")
    print(f"Oscillator 1 seed: {osc1_seed}")
    print(f"Oscillator 2 seed: {osc2_seed}")

    # --- Combined simulation ---
    grid_combined = make_grid(osc1_seed + osc2_seed)
    print(f"\n--- Combined simulation ({STEPS} steps) ---")
    pos_hist, shape_hist, bit_counts = run_simulation(grid_combined, rule, STEPS)

    # --- Reference single-oscillator simulations ---
    grid_osc1 = make_grid(osc1_seed)
    _, _, bc1 = run_simulation(grid_osc1, rule, STEPS)
    pos_hist_1, _, _ = run_simulation(make_grid(osc1_seed), rule, STEPS)

    grid_osc2 = make_grid(osc2_seed)
    pos_hist_2, _, _ = run_simulation(make_grid(osc2_seed), rule, STEPS)

    # --- Find interaction step ---
    # First step where a bit from osc1 reference is in neighborhood of a bit from osc2 reference
    interaction_step = -1
    for t in range(STEPS + 1):
        s1 = set(pos_hist_1[t])
        s2 = set(pos_hist_2[t])
        if any_neighbor_in_set(s1, s2):
            interaction_step = t
            break

    print(f"\nInteraction step (neighbor proximity): {interaction_step}")

    # --- Print step-by-step summary ---
    print(f"\nStep-by-step bit counts:")
    for t in range(0, min(20, STEPS + 1)):
        clusters = cluster_count(pos_hist[t])
        print(f"  t={t:3d}  bits={bit_counts[t]}  clusters={clusters}  pos={pos_hist[t]}")
    print("  ...")
    for t in range(180, STEPS + 1):
        clusters = cluster_count(pos_hist[t])
        print(f"  t={t:3d}  bits={bit_counts[t]}  clusters={clusters}")

    # --- Analyze results ---
    is_bit_conserving = all(c == initial_bits for c in bit_counts)
    print(f"\nis_bit_conserving: {is_bit_conserving}")
    print(f"bit_counts min/max: {min(bit_counts)}/{max(bit_counts)}")

    outcome_class = classify_outcome(
        bit_counts, pos_hist, shape_hist,
        pos_hist_1, pos_hist_2, interaction_step
    )
    print(f"outcome_class: {outcome_class}")

    # Final state analysis
    final_pos = pos_hist[-1]
    final_clusters = cluster_count(final_pos)
    period = detect_period(shape_hist, start=150, max_period=50)
    print(f"final clusters: {final_clusters}, period: {period}")
    print(f"final positions: {final_pos}")

    # Build summary
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

    return 0 if is_bit_conserving else 1


if __name__ == "__main__":
    sys.exit(main())

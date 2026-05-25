#!/usr/bin/env python3
"""
coherence_testing.py — Three-test coherence verification protocol.

Tests whether a multi-bit pattern is a genuine glider (coherent interacting
object) or a non-interacting composite of independent bits.

Test A (Decomposition): Run each constituent bit independently; check whether
the multi-bit trajectory matches the bitwise superposition of solo trajectories.
If yes, the bits do NOT interact → non-interacting composite.

Test B (Collision Interaction): Count cells containing >1 occupied channel
across the simulation. Zero multi-bit cells means bits never occupy the same
spatial cell → non-interacting composite.

Test C (Bit-Removal Stability): Remove one bit at a time. If the remaining
pattern remains stable (same velocity, conserved bit count, bounded extent),
then the removed bit was non-essential → non-interacting composite.
If removal destabilizes the pattern, the bits are interdependent.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import stream, collide
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent


def sim_bits(particle, lut, L=32, steps=32):
    """
    Simulate a particle for `steps` steps.

    Returns a list of tuples:
        (grid_copy, com_vector, extent_tuple, total_bits)
    for each step (including initial state at step 0).
    """
    grid = seed_grid(L, particle)
    bits0 = int(grid.sum())
    out = [(grid.copy(), compute_com_circular(grid)[0], bounding_extent(grid), bits0)]
    for _ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
        out.append((grid.copy(), compute_com_circular(grid)[0], bounding_extent(grid), int(grid.sum())))
    return out


def get_velocity(history, L, steps):
    """
    Compute mean velocity vector from a simulation history.

    Args:
        history: output of sim_bits() — list of (grid, com, extent, bits)
        L: grid size
        steps: number of evolution steps

    Returns:
        np.ndarray of shape (3,) with mean velocity per step, or None if
        center-of-mass is lost at any point.
    """
    cd = np.zeros(3)
    for i in range(1, len(history)):
        c0, c1 = history[i - 1][1], history[i][1]
        if c0 is None or c1 is None:
            return None
        d = c1 - c0
        for a in range(3):
            if d[a] > L / 2:
                d[a] -= L
            elif d[a] < -L / 2:
                d[a] += L
        cd += d
    return cd / steps


def _count_multi_bit_cells(grids):
    """Count total cells with >1 bit across all steps in a history."""
    total = 0
    for grid, _, _, _ in grids:
        packed = np.zeros(grid.shape[:3], dtype=np.uint16)
        for ch in range(12):
            packed |= (grid[..., ch].astype(np.uint16) << ch)
        counts = np.zeros(grid.shape[:3], dtype=np.int32)
        for ch in range(12):
            counts += ((packed >> ch) & 1).astype(np.int32)
        total += int((counts > 1).sum())
    return total


def test_decomposition(particle, lut, L=32, steps=32, atol=0.01):
    """
    Test A — Single-bit decomposition coherence.

    Runs each individual bit of `particle` independently and compares the
    solo velocity to the full multi-bit velocity. If ALL solo velocities match
    the full velocity, the particle is a non-interacting composite.

    Returns:
        dict with:
            "pass": bool — True if the test PROVES non-interacting composite
            "single_bit_matches": bool — whether all solo velocities match
            "full_velocity": np.ndarray or None
            "solo_velocities": list of np.ndarray or None
    """
    particle = [tuple(c) for c in particle]
    full_hist = sim_bits(particle, lut, L, steps)
    full_vel = get_velocity(full_hist, L, steps)

    single_bit_matches = True
    solo_velocities = []

    for bit in particle:
        solo_hist = sim_bits([bit], lut, L, steps)
        solo_vel = get_velocity(solo_hist, L, steps)
        solo_velocities.append(solo_vel)
        if solo_vel is None or full_vel is None:
            single_bit_matches = False
            break
        if not np.allclose(solo_vel, full_vel, atol=atol):
            single_bit_matches = False
            break

    return {
        "pass": bool(single_bit_matches),
        "single_bit_matches": bool(single_bit_matches),
        "full_velocity": full_vel,
        "solo_velocities": solo_velocities,
    }


def test_collision_interaction(particle, lut, L=32, steps=32):
    """
    Test B — Collision interaction coherence.

    Counts cells that contain more than one bit across the simulation run.
    A count of zero means bits never occupy the same spatial cell, proving
    they are non-interacting.

    Returns:
        dict with:
            "pass": bool — True if test PROVES non-interacting composite (count==0)
            "multi_bit_cell_count": int
            "full_velocity": np.ndarray or None
    """
    particle = [tuple(c) for c in particle]
    full_hist = sim_bits(particle, lut, L, steps)
    full_vel = get_velocity(full_hist, L, steps)
    count = _count_multi_bit_cells(full_hist)

    return {
        "pass": (count == 0),
        "multi_bit_cell_count": int(count),
        "full_velocity": full_vel,
    }


def test_bit_removal(particle, lut, L=32, steps=32, atol=0.01, extent_cap=6):
    """
    Test C — Bit-removal stability.

    Removes each bit in turn and checks whether the remaining pattern stays
    stable (same velocity, bit conservation, bounded extent).
    If removing ANY bit does NOT destabilize the pattern, the original was a
    non-interacting composite. If ALL removals destabilize it, the bits are
    interdependent (genuine glider).

    Returns:
        dict with:
            "pass": bool — True if test PROVES genuine glider (all removals destabilize)
            "bit_removal_destabilizes": bool — whether every removal destabilizes
            "sub_results": list of dicts, one per removed bit
    """
    particle = [tuple(c) for c in particle]
    full_hist = sim_bits(particle, lut, L, steps)
    full_vel = get_velocity(full_hist, L, steps)

    sub_results = []
    all_destabilize = True

    for i in range(len(particle)):
        sub = particle[:i] + particle[i + 1:]
        sub_hist = sim_bits(sub, lut, L, steps)
        sub_vel = get_velocity(sub_hist, L, steps)

        # Determine if this removal destabilizes the pattern
        destabilized = False
        reasons = []

        # Check bit conservation
        expected_bits = len(sub)
        for _, _, _, bc in sub_hist:
            if bc != expected_bits:
                destabilized = True
                reasons.append("bit_loss")
                break

        # Check extent cap
        if not destabilized:
            for _, _, ext, _ in sub_hist:
                if max(ext) > extent_cap:
                    destabilized = True
                    reasons.append("extent_exceeded")
                    break

        # Check velocity match (if still stable, it's not destabilized)
        if not destabilized:
            if sub_vel is None or full_vel is None:
                destabilized = True
                reasons.append("com_lost")
            elif not np.allclose(sub_vel, full_vel, atol=atol):
                destabilized = True
                reasons.append("velocity_changed")

        if not destabilized:
            all_destabilize = False

        sub_results.append({
            "removed_index": i,
            "removed_bit": particle[i],
            "destabilizes": bool(destabilized),
            "reasons": reasons,
            "sub_velocity": sub_vel,
        })

    return {
        "pass": bool(all_destabilize),
        "bit_removal_destabilizes": bool(all_destabilize),
        "sub_results": sub_results,
        "full_velocity": full_vel,
    }


def run_all_tests(particle, lut, L=32, steps=32, atol=0.01, extent_cap=6):
    """
    Run the full three-test coherence protocol.

    Returns:
        dict with results from all three tests plus a composite verdict.

    Verdict rules:
        - NON_INTERACTING_COMPOSITE: passes Test A or Test B
        - GENUINE_GLIDER: fails Test A AND Test B, passes Test C
        - UNSTABLE: full velocity is None (COM lost before steps complete)
        - INDETERMINATE: everything else
    """
    t1 = test_decomposition(particle, lut, L, steps, atol)
    t2 = test_collision_interaction(particle, lut, L, steps)
    t3 = test_bit_removal(particle, lut, L, steps, atol, extent_cap)

    if t1["full_velocity"] is None:
        verdict = "UNSTABLE"
    elif t1["pass"] and t2["pass"]:
        verdict = "NON_INTERACTING_COMPOSITE"
    elif not t1["pass"] and not t2["pass"] and t3["pass"]:
        verdict = "GENUINE_GLIDER"
    else:
        verdict = "INDETERMINATE"

    return {
        "test_A_decomposition": t1,
        "test_B_collision_interaction": t2,
        "test_C_bit_removal": t3,
        "verdict": verdict,
        "L": L,
        "steps": steps,
        "particle": [list(c) for c in particle],
    }


if __name__ == "__main__":
    import json

    # Positive control: LUT-08 reference glider
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        ref = json.load(f)
    lut08 = np.array(ref["lut"], dtype=np.uint16)
    ref_particle = [tuple(c) for c in ref["particle"]]

    print("Running three-test coherence protocol on LUT-08 reference glider...")
    results = run_all_tests(ref_particle, lut08, L=32, steps=32)
    print(f"Verdict: {results['verdict']}")
    print(f"  Test A (decomposition pass={results['test_A_decomposition']['pass']}): "
          f"single_bit_matches={results['test_A_decomposition']['single_bit_matches']}")
    print(f"  Test B (collision pass={results['test_B_collision_interaction']['pass']}): "
          f"multi_bit_cells={results['test_B_collision_interaction']['multi_bit_cell_count']}")
    print(f"  Test C (bit-removal pass={results['test_C_bit_removal']['pass']}): "
          f"destabilizes={results['test_C_bit_removal']['bit_removal_destabilizes']}")

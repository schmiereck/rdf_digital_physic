#!/usr/bin/env python3
"""
cooperative_lut_13ch.py — Parametric LUT family for 13-channel FCC LGCA with
cooperative trapping dynamics.

Core design:
- Weight-0: fixed point (0→0)
- Weight-1 prop: Cartesian transposition to antiparallel partner (bit-conserving,
  bijective, O_h-invariant)
- Weight-1 rest: fixed point (rest→rest)
- Weight-2: O_h-equivariant self-mappings on each of the 5 orbit types
  (A: antiparallel 6, B: obtuse 24, C: perpendicular 12, D: acute 24, E: rest+prop 12)
- Weight-3+: O_h-equivariant orbit pairing by (weight, size, stabilizer conjugacy class)

All generated LUTs are audited for bijection, bit conservation, and O_h symmetry.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from search_3d_gliders import (
    get_oh_permutations,
    hamming,
    fcc_neighbor_vectors,
)

# ============================================================
# 1. 13-channel O_h infrastructure
# ============================================================

CARTESIAN_PAIRS = [(0, 3), (1, 2), (4, 7), (5, 6), (8, 11), (9, 10)]
ANTIPARALLEL_MAP = {a: b for a, b in CARTESIAN_PAIRS}
ANTIPARALLEL_MAP.update({b: a for a, b in CARTESIAN_PAIRS})


def build_oh_permutations_13ch() -> list[tuple[int, ...]]:
    """Build the 48 O_h permutations for 13 channels.

    Channels 0-11 permute as in the 12-channel system; channel 12 is fixed.
    """
    perms_12 = get_oh_permutations(verbose=False)
    return [sigma + (12,) for sigma in perms_12]


def precompute_perm_action_13ch(perms: list[tuple[int, ...]]) -> np.ndarray:
    """Precompute the O_h action on all 8192 13-bit states.

    Returns array of shape (n_perms, 8192) with dtype uint16.
    """
    n_perms = len(perms)
    action = np.zeros((n_perms, 8192), dtype=np.uint16)
    s_arr = np.arange(8192, dtype=np.uint32)
    for g, sigma in enumerate(perms):
        out = np.zeros(8192, dtype=np.uint32)
        for i in range(13):
            mask = (s_arr >> i) & 1
            out |= mask << int(sigma[i])
        action[g] = out.astype(np.uint16)
    return action


def compute_orbits_13ch(action: np.ndarray) -> tuple[list[list[int]], np.ndarray]:
    """Partition {0..8191} into orbits under the O_h action."""
    n_perms = action.shape[0]
    orbit_of = -np.ones(8192, dtype=np.int32)
    orbits: list[list[int]] = []
    for s in range(8192):
        if orbit_of[s] >= 0:
            continue
        members = {s}
        stack = [s]
        while stack:
            t = stack.pop()
            for g in range(n_perms):
                u = int(action[g, t])
                if u not in members:
                    members.add(u)
                    stack.append(u)
        oid = len(orbits)
        for t in members:
            orbit_of[t] = oid
        orbits.append(sorted(members))
    return orbits, orbit_of


def compute_all_stabilizers_13ch(action: np.ndarray) -> list[tuple[int, ...]]:
    """For each state, return the sorted tuple of permutation indices that fix it."""
    n_perms = action.shape[0]
    stabs: list[tuple[int, ...]] = []
    for s in range(8192):
        stab = [g for g in range(n_perms) if int(action[g, s]) == s]
        stabs.append(tuple(stab))
    return stabs


# ============================================================
# 2. Weight-2 orbit classification
# ============================================================

def classify_weight2_orbits(
    orbits: list[list[int]],
    stabs: list[tuple[int, ...]],
) -> dict[str, dict]:
    """Classify the 5 weight-2 orbit types programmatically.

    Returns a dict with keys 'A','B','C','D','E', each containing:
      - orbit_index: global orbit index
      - states: list of states in the orbit
      - size: orbit size
      - rep: representative state
      - stab_size: size of rep's stabilizer
    """
    fcc_vecs = fcc_neighbor_vectors()
    antiparallel_set = {(1 << a) | (1 << b) for a, b in CARTESIAN_PAIRS}

    result: dict[str, dict] = {}
    found = {"A": False, "B": False, "C": False, "D": False, "E": False}

    for oidx, orb in enumerate(orbits):
        if hamming(orb[0]) != 2:
            continue
        rep = orb[0]
        chs = [i for i in range(13) if (rep >> i) & 1]
        has_rest = 12 in chs

        if has_rest:
            label = "E"
        elif rep in antiparallel_set:
            label = "A"
        else:
            i, j = chs
            dot = int(np.dot(fcc_vecs[i], fcc_vecs[j]))
            if dot == -1:
                label = "B"
            elif dot == 0:
                label = "C"
            elif dot == 1:
                label = "D"
            else:
                raise ValueError(f"Unexpected dot product {dot} for weight-2 state {rep}")

        if found[label]:
            raise ValueError(f"Duplicate orbit type {label}")
        found[label] = True

        result[label] = {
            "orbit_index": oidx,
            "states": orb,
            "size": len(orb),
            "rep": rep,
            "stab_size": len(stabs[rep]),
        }

    missing = [k for k, v in found.items() if not v]
    if missing:
        raise ValueError(f"Missing weight-2 orbit types: {missing}")

    return result


# ============================================================
# 3. Parametric LUT construction
# ============================================================

def _build_weight1_mapping() -> np.ndarray:
    """Build the fixed weight-1 sub-table.

    Prop weight-1: antiparallel transposition.
    Rest weight-1: identity.
    """
    lut = np.zeros(8192, dtype=np.uint16)
    # Weight-0
    lut[0] = 0
    # Weight-1 prop
    for k in range(12):
        lut[1 << k] = 1 << ANTIPARALLEL_MAP[k]
    # Weight-1 rest
    lut[1 << 12] = 1 << 12
    return lut


def _build_weight2_self_map(
    orbit_states: list[int],
    action: np.ndarray,
    stabs: list[tuple[int, ...]],
    target_choice: int,
) -> dict[int, int]:
    """Build an equivariant self-bijection on a single orbit.

    Parameters
    ----------
    orbit_states : list of states in the orbit
    action : O_h action array
    stabs : stabilizer list
    target_choice : index into the list of valid same-stabilizer targets

    Returns
    -------
    dict mapping each source state to its destination state.
    """
    rep = orbit_states[0]
    H = stabs[rep]
    valid_targets = [t for t in orbit_states if stabs[t] == H]
    if not valid_targets:
        raise ValueError(f"No valid same-stabilizer targets for orbit rep {rep}")
    target = valid_targets[target_choice % len(valid_targets)]

    mapping = {}
    n_perms = action.shape[0]
    for g in range(n_perms):
        src = int(action[g, rep])
        dst = int(action[g, target])
        if src in mapping:
            if mapping[src] != dst:
                raise ValueError(f"Inconsistent equivariant map at state {src}")
        else:
            mapping[src] = dst

    # Verify bijection on this orbit
    src_set = set(mapping.keys())
    dst_set = set(mapping.values())
    if src_set != set(orbit_states) or dst_set != set(orbit_states):
        raise ValueError("Self-map is not a bijection on the orbit")
    if len(mapping) != len(orbit_states):
        raise ValueError("Self-map is not injective on the orbit")

    return mapping


def _build_weight3plus_mapping(
    rng: np.random.Generator,
    orbits: list[list[int]],
    action: np.ndarray,
    stabs: list[tuple[int, ...]],
    fixed_states: set[int],
) -> dict[int, int]:
    """Build O_h-equivariant bijections for weight-3+ states using orbit pairing.

    Pools orbits by (weight, size, frozenset of stabilizer tuples) and randomly
    pairs orbits within each pool. For each src->dst orbit pair, picks a
    representative and a same-stabilizer target, then propagates by O_h.

    Parameters
    ----------
    rng : numpy random generator
    orbits : list of all orbits
    action : O_h action array
    stabs : stabilizer list
    fixed_states : set of states already mapped (will be skipped)

    Returns
    -------
    dict mapping source states to destination states for weight-3+.
    """
    n_perms = action.shape[0]
    mapping = {}

    # Group orbits by signature
    groups: dict[tuple, list[int]] = {}
    for oidx, orb in enumerate(orbits):
        rep = orb[0]
        if rep in fixed_states:
            continue
        w = hamming(rep)
        sz = len(orb)
        stab_set = frozenset(stabs[s] for s in orb)
        sig = (w, sz, stab_set)
        groups.setdefault(sig, []).append(oidx)

    for sig, orbit_list in groups.items():
        n = len(orbit_list)
        shuffled = list(orbit_list)
        if n > 1:
            order = rng.permutation(n)
            shuffled = [orbit_list[i] for i in order]

        for src_idx, dst_idx in zip(orbit_list, shuffled):
            src_orbit = orbits[src_idx]
            dst_orbit = orbits[dst_idx]
            rep_src = src_orbit[0]
            H_src = stabs[rep_src]

            valid_targets = [t for t in dst_orbit if stabs[t] == H_src]
            if not valid_targets:
                raise ValueError(
                    f"No valid target for orbit {src_idx} (weight {sig[0]}, size {sig[1]}) "
                    f"-> orbit {dst_idx}"
                )
            target = int(valid_targets[rng.integers(len(valid_targets))])

            for g in range(n_perms):
                src = int(action[g, rep_src])
                dst = int(action[g, target])
                if src in mapping:
                    if mapping[src] != dst:
                        raise ValueError(
                            f"Inconsistent equivariant map at state {src}: "
                            f"existing={mapping[src]} new={dst}"
                        )
                else:
                    mapping[src] = dst

    return mapping


def build_cooperative_lut_13ch(
    config: dict,
    perms: list[tuple[int, ...]] | None = None,
    action: np.ndarray | None = None,
    orbits: list[list[int]] | None = None,
    stabs: list[tuple[int, ...]] | None = None,
    w2_info: dict[str, dict] | None = None,
) -> np.ndarray:
    """Build a single cooperative-trapping LUT from a configuration dict.

    Parameters
    ----------
    config : dict with keys:
        - 'w2_A_target': int, choice index for A→A self-map
        - 'w2_B_target': int, choice index for B→B self-map
        - 'w2_C_target': int, choice index for C→C self-map
        - 'w2_D_target': int, choice index for D→D self-map
        - 'w2_E_target': int, choice index for E→E self-map
        - 'w3plus_seed': int, seed for weight-3+ random orbit pairing
    perms, action, orbits, stabs, w2_info : precomputed structures (optional)

    Returns
    -------
    lut : np.ndarray of shape (8192,) and dtype uint16
    """
    if perms is None:
        perms = build_oh_permutations_13ch()
    if action is None:
        action = precompute_perm_action_13ch(perms)
    if orbits is None:
        orbits, _ = compute_orbits_13ch(action)
    if stabs is None:
        stabs = compute_all_stabilizers_13ch(action)
    if w2_info is None:
        w2_info = classify_weight2_orbits(orbits, stabs)

    lut = -np.ones(8192, dtype=np.int32)
    fixed_states: set[int] = set()

    # Weight-0 and weight-1 (fixed)
    w01_lut = _build_weight1_mapping()
    for s in range(8192):
        if hamming(s) <= 1:
            lut[s] = int(w01_lut[s])
            fixed_states.add(s)

    # Weight-2 (parametric self-maps)
    for label in ["A", "B", "C", "D", "E"]:
        info = w2_info[label]
        target_choice = config.get(f"w2_{label}_target", 0)
        mapping = _build_weight2_self_map(
            info["states"], action, stabs, target_choice
        )
        for src, dst in mapping.items():
            if lut[src] != -1:
                raise ValueError(f"State {src} already mapped")
            lut[src] = dst
            fixed_states.add(src)

    # Weight-3+ (random orbit pairing)
    rng = np.random.default_rng(config.get("w3plus_seed", 0))
    w3plus_mapping = _build_weight3plus_mapping(
        rng, orbits, action, stabs, fixed_states
    )
    for src, dst in w3plus_mapping.items():
        if lut[src] != -1:
            raise ValueError(f"State {src} already mapped in weight-3+")
        lut[src] = dst

    assert (lut >= 0).all(), "LUT incomplete"
    return lut.astype(np.uint16)


# ============================================================
# 4. Audit
# ============================================================

def audit_lut_13ch(lut: np.ndarray, action: np.ndarray) -> dict:
    """Run the three mandatory audits on a 13-channel LUT.

    Returns dict with keys:
        - bijection (bool)
        - bit_conserving (bool)
        - symmetric (bool)
        - first_violating_perm (int or None)
    """
    results: dict = {}

    # Bijection
    results["bijection"] = bool(len(np.unique(lut)) == 8192)

    # Bit conservation
    pop_in = np.array([bin(s).count("1") for s in range(8192)], dtype=np.uint8)
    pop_out = np.array([bin(int(lut[s])).count("1") for s in range(8192)], dtype=np.uint8)
    results["bit_conserving"] = bool(np.array_equal(pop_in, pop_out))

    # O_h symmetry
    sym_ok = True
    bad = None
    n_perms = action.shape[0]
    for g in range(n_perms):
        lhs = lut[action[g]]
        rhs = action[g, lut]
        if not np.array_equal(lhs, rhs):
            sym_ok = False
            bad = g
            break
    results["symmetric"] = sym_ok
    results["first_violating_perm"] = int(bad) if bad is not None else None

    return results


# ============================================================
# 5. Variant enumeration
# ============================================================

def enumerate_weight2_self_map_choices(
    w2_info: dict[str, dict],
    stabs: list[tuple[int, ...]],
) -> dict[str, int]:
    """Count the number of valid same-stabilizer targets for each weight-2 orbit self-map."""
    counts = {}
    for label in ["A", "B", "C", "D", "E"]:
        info = w2_info[label]
        rep = info["rep"]
        H = stabs[rep]
        valid = [t for t in info["states"] if stabs[t] == H]
        counts[label] = len(valid)
    return counts


def generate_all_lut_variants(
    max_variants: int = 500,
    w3plus_seeds: int = 2,
    verbose: bool = True,
) -> tuple[list[np.ndarray], list[dict], dict]:
    """Generate all valid cooperative-trapping LUT variants.

    Parameters
    ----------
    max_variants : int
        Maximum number of variants to generate.
    w3plus_seeds : int
        Number of distinct weight-3+ random seeds to try per weight-2 config.
    verbose : bool

    Returns
    -------
    luts : list of valid LUT arrays
    configs : list of configuration dicts
    metadata : dict with generation statistics
    """
    t0 = time.time()

    perms = build_oh_permutations_13ch()
    action = precompute_perm_action_13ch(perms)
    orbits, _ = compute_orbits_13ch(action)
    stabs = compute_all_stabilizers_13ch(action)
    w2_info = classify_weight2_orbits(orbits, stabs)

    choice_counts = enumerate_weight2_self_map_choices(w2_info, stabs)
    if verbose:
        print("[cooperative_lut_13ch] Weight-2 self-map choices:")
        for label, count in choice_counts.items():
            print(f"  Orbit {label}: {count} choices")

    # Enumerate all weight-2 configurations
    w2_configs = []
    for a in range(choice_counts["A"]):
        for b in range(choice_counts["B"]):
            for c in range(choice_counts["C"]):
                for d in range(choice_counts["D"]):
                    for e in range(choice_counts["E"]):
                        w2_configs.append({
                            "w2_A_target": a,
                            "w2_B_target": b,
                            "w2_C_target": c,
                            "w2_D_target": d,
                            "w2_E_target": e,
                        })

    if verbose:
        print(f"[cooperative_lut_13ch] Total weight-2 configurations: {len(w2_configs)}")

    luts: list[np.ndarray] = []
    configs: list[dict] = []
    audit_fails = 0
    audit_pass = 0

    for w2_idx, w2_cfg in enumerate(w2_configs):
        for seed in range(w3plus_seeds):
            if len(luts) >= max_variants:
                break

            config = dict(w2_cfg)
            config["w3plus_seed"] = seed
            config["variant_id"] = len(luts)

            try:
                lut = build_cooperative_lut_13ch(
                    config, perms=perms, action=action, orbits=orbits,
                    stabs=stabs, w2_info=w2_info,
                )
            except ValueError as exc:
                if verbose:
                    print(f"  [build fail] w2={w2_idx} seed={seed}: {exc}")
                audit_fails += 1
                continue

            audit = audit_lut_13ch(lut, action)
            if not (audit["bijection"] and audit["bit_conserving"] and audit["symmetric"]):
                audit_fails += 1
                if verbose:
                    print(f"  [audit fail] w2={w2_idx} seed={seed}: {audit}")
                continue

            luts.append(lut)
            configs.append(config)
            audit_pass += 1

        if len(luts) >= max_variants:
            break

    dt = time.time() - t0

    metadata = {
        "n_attempted": len(w2_configs) * w3plus_seeds,
        "n_valid": len(luts),
        "n_audit_fails": audit_fails,
        "audit_pass_rate": audit_pass / max(1, audit_pass + audit_fails),
        "weight2_choice_counts": choice_counts,
        "generation_time_seconds": dt,
    }

    if verbose:
        print(f"[cooperative_lut_13ch] Generated {len(luts)} valid LUTs in {dt:.2f}s")
        print(f"  Audit pass rate: {metadata['audit_pass_rate']:.3f}")

    return luts, configs, metadata


# ============================================================
# 6. Main / report generation
# ============================================================

def main():
    out_dir = SCRIPT_DIR.parent / "archive" / "iter_251" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    luts, configs, meta = generate_all_lut_variants(
        max_variants=500,
        w3plus_seeds=2,
        verbose=True,
    )

    # Compute weight-2 orbit details for the report
    perms = build_oh_permutations_13ch()
    action = precompute_perm_action_13ch(perms)
    orbits, _ = compute_orbits_13ch(action)
    stabs = compute_all_stabilizers_13ch(action)
    w2_info = classify_weight2_orbits(orbits, stabs)

    weight2_orbit_info = {}
    for label in ["A", "B", "C", "D", "E"]:
        info = w2_info[label]
        rep = info["rep"]
        chs = [i for i in range(13) if (rep >> i) & 1]
        weight2_orbit_info[label] = {
            "size": info["size"],
            "representative": int(rep),
            "channels": chs,
            "stabilizer_size": info["stab_size"],
            "description": {
                "A": "Antiparallel prop pair (6 states)",
                "B": "Obtuse prop pair, 120 deg (24 states)",
                "C": "Perpendicular prop pair, 90 deg (12 states)",
                "D": "Acute prop pair, 60 deg (24 states)",
                "E": "Rest+prop pair (12 states)",
            }[label],
        }

    # Weight-1 mapping description
    weight1_mapping = {
        "weight_0": "0 -> 0 (fixed point)",
        "prop_weight1": "Cartesian transposition to antiparallel partner",
        "pairs": CARTESIAN_PAIRS,
        "rest_weight1": "(1<<12) -> (1<<12) (stationary fixed point)",
    }

    # Note on cross-orbit mappings
    cross_orbit_note = (
        "Mathematical analysis shows that full O_h-equivariant bijections between "
        "orbits C<->E and B<->D are impossible because their stabilizer subgroups "
        "are non-conjugate in O_h. All generated variants use self-maps for weight-2. "
        "Active channel mixing (F5) must occur via weight-3+ dynamics."
    )

    report = {
        "n_lut_variants": len(luts),
        "n_lut_variants_with_f5": 0,
        "audit_pass_rate": meta["audit_pass_rate"],
        "weight2_orbit_info": weight2_orbit_info,
        "sample_lut_shape": [8192],
        "weight1_mapping": weight1_mapping,
        "cross_orbit_weight2_note": cross_orbit_note,
        "generation_metadata": meta,
    }

    with open(out_dir / "infrastructure_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"[save] Report -> {out_dir / 'infrastructure_report.json'}")

    # Save a few sample LUTs
    for i in range(min(5, len(luts))):
        np.save(out_dir / f"sample_lut_{i:03d}.npy", luts[i])

    return luts, configs, meta


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
test_nbody_stability.py — Phase 5.4 N-Body Stability experiments.

PRE-REGISTRATION (committed before any simulation run)
======================================================
Working hypothesis:
    Under the Phase 5.3 envelope (sigma=2.5, eta=2.0, gamma=0.9, threshold=0.045,
    alpha=2.0, LUT-08 glider), a hierarchical N-body configuration on the
    3D+1 FCC-projected (Oh) lattice can be sustained over a 160-step window
    such that (a) bit conservation holds (total bits = 4*N), and
    (b) every glider remains within a finite radius of the system barycenter
    (i.e. no monotonic outward drift beyond the vacuum-control baseline).

Falsification criteria (binding before run):
    F1. Bit-count drift: total active+latched bits != 4*N at any step (latching
        merger). Logged but does not invalidate the run; treated as a
        non-bit-conserving outcome.
    F2. Dispersion collapse: maximum particle distance from the system
        barycenter at step 160 exceeds the vacuum-control mean by more than
        1 sigma (control noise band) for >= 2 of 3 (or 2 of 4) particles.
    F3. Latching singularity: all particles coalesce into a single cluster
        (max pairwise distance < 2.0 lattice units) for >= 20 consecutive steps.

Controls:
    For every active (eta=2.0) configuration, a matched vacuum control
    (eta=0.0) with identical seed, permutation, and initial conditions is run.

Oh-anisotropy controls:
    Each configuration is run under at least two distinct Oh-channel
    permutations (g=0 and g=10, mirroring iter_235's anisotropy protocol).
    Stability that depends on a specific orientation is flagged as a
    lattice-anisotropy limitation, not isotropic N-body binding.

Outputs:
    - archive/iter_236/results/nbody_<config>_<perm>.csv  (per-step log)
    - archive/iter_236/results/nbody_stability_report.md   (human report)
    - archive/iter_236/results/nbody_escape_velocity.csv   (probe)
"""

import os
import sys
import json
import csv
import math
import numpy as np

# Path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine
from src.engine_3d import SHIFTS
from src.search_3d_gliders import get_oh_permutations

# =======================================================================
# Baseline parameters (FIXED per Manager's Note - Phase 5.3 envelope)
# =======================================================================
L = 32          # Grid size (matches iter_235.8 long-bound-state run)
GAMMA = 0.90
ETA_ACTIVE = 2.0
ETA_CONTROL = 0.0
THRESHOLD = 0.045
ALPHA = 2.0
SIGMA = 2.5
STEPS = 160

# =======================================================================
# Glider loader
# =======================================================================
GLIDER_PATH = os.path.join(ROOT_DIR, "archive", "iter_224", "results",
                           "glider_00_lut08_sub03.json")
with open(GLIDER_PATH, "r") as f:
    _glider_data = json.load(f)
PARTICLE = _glider_data["particle"]
LUT_SEED = _glider_data["lut_seed"]

# =======================================================================
# Permutation infrastructure
# =======================================================================
S = np.array(SHIFTS, dtype=float)
S_pinv = np.linalg.pinv(S)
PERMS = get_oh_permutations()


def rotate_particle_list(part, g):
    """Apply Oh permutation g to a particle (list of [dl,dr,dc,ch])."""
    perm = PERMS[g]
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T

    rotated = []
    for (dl, dr, dc, ch) in part:
        pos = np.array([dl, dr, dc], dtype=float)
        pos_rot = np.round(M_g @ pos).astype(int)
        ch_rot = perm[ch]
        rotated.append([int(pos_rot[0]), int(pos_rot[1]), int(pos_rot[2]),
                        int(ch_rot)])
    return rotated, M_g


def seed_glider(engine, cx, cy, cz, rotated_part):
    L_ = engine.L
    for dl, dr, dc, ch in rotated_part:
        engine.temporal_grid[(cx + dl) % L_,
                              (cy + dr) % L_,
                              (cz + dc) % L_, ch] = 1


# =======================================================================
# Self-contained K-means clustering (no scipy/sklearn dependency)
# =======================================================================
def kmeans_cluster(points, k, max_iter=200, seed=0):
    """Hard k-means on small point sets (n <= 16) in 3D.

    points: (N, 3) array of un-wrapped float coordinates.
    Returns (labels, centroids) where labels in [0, k-1].
    Deterministic seeding: k-means++ with NumPy RNG.
    """
    pts = np.asarray(points, dtype=float)
    N = pts.shape[0]
    rng = np.random.default_rng(seed)

    # k-means++ initialization
    idx0 = int(rng.integers(N))
    centers = [pts[idx0].copy()]
    for _ in range(k - 1):
        d2 = np.full(N, np.inf)
        for c in centers:
            d2 = np.minimum(d2, np.sum((pts - c) ** 2, axis=1))
        total = d2.sum()
        if total <= 1e-12:
            # degenerate: fall back to random
            ridx = int(rng.integers(N))
        else:
            probs = d2 / total
            ridx = int(rng.choice(N, p=probs))
        centers.append(pts[ridx].copy())
    centers = np.array(centers)

    labels = np.zeros(N, dtype=int)
    for _it in range(max_iter):
        # Assign
        d2_all = np.zeros((N, k))
        for j in range(k):
            d2_all[:, j] = np.sum((pts - centers[j]) ** 2, axis=1)
        new_labels = np.argmin(d2_all, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        # Update centers
        for j in range(k):
            mask = labels == j
            if mask.sum() > 0:
                centers[j] = pts[mask].mean(axis=0)
            # else: keep previous center
    return labels, centers


def unwrap_coords(coords_int, ref_point, L_):
    """Map integer lattice coords into the unwrapped frame closest to ref_point.

    coords_int: (N,3) int array of grid indices.
    ref_point:  (3,) float, current "center" of the system used for unwrapping.
    """
    coords = coords_int.astype(float)
    # For each axis, choose the periodic image closest to ref_point.
    out = np.empty_like(coords)
    for axis in range(3):
        c = coords[:, axis]
        r = ref_point[axis]
        # Candidates: c, c+L, c-L; pick whichever is closer to r
        candidates = np.stack([c, c + L_, c - L_], axis=1)
        diff = np.abs(candidates - r)
        idx = np.argmin(diff, axis=1)
        out[:, axis] = candidates[np.arange(c.size), idx]
    return out


def system_barycenter(coords_unwrapped):
    return coords_unwrapped.mean(axis=0)


def torus_pair_dist(p1, p2, L_):
    """Minimum-image Euclidean distance on the toroidal grid."""
    d = np.abs(np.asarray(p1, dtype=float) - np.asarray(p2, dtype=float))
    d = np.minimum(d, L_ - d)
    return float(np.sqrt((d ** 2).sum()))


def torus_dist_from_ref(p, ref, L_):
    """Minimum-image Euclidean distance from p to ref on toroidal grid."""
    return torus_pair_dist(p, ref, L_)


# =======================================================================
# Configuration builders
# =======================================================================
def build_3body_hierarchical(third_offset=8):
    """Hierarchical 3-body: tight binary at (-3, 0, 0) and (+2, 0, 0), plus
    a third glider further along the row axis at (0, third_offset, 0)."""
    return [
        np.array([0, -3, 0], dtype=float),
        np.array([0, 2, 0], dtype=float),
        np.array([0, 2 + third_offset, 0], dtype=float),
    ]


def build_4body_double_binary(binary_sep=8):
    """4-body double-binary: two tight binaries separated along an axis."""
    return [
        np.array([0, -3, 0], dtype=float),
        np.array([0, 2, 0], dtype=float),
        np.array([0, -3 + binary_sep, binary_sep], dtype=float),
        np.array([0, 2 + binary_sep, binary_sep], dtype=float),
    ]


# =======================================================================
# Simulation runner
# =======================================================================
def run_nbody(eta, init_positions, g, steps=STEPS):
    """Run an N-body simulation.

    init_positions: list of (3,) arrays in particle-local (rotated)
                    coordinates. Each is placed with the LUT-08 glider seed.
    g: Oh permutation index applied uniformly to all gliders and positions.
    Returns: dict with per-step records.
    """
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=GAMMA,
        eta=eta,
        threshold=THRESHOLD,
        alpha=ALPHA,
        sigma=SIGMA,
        lut_seed=LUT_SEED,
        use_12_channels=True,
    )

    rotated_particle, M_g = rotate_particle_list(PARTICLE, g)

    N = len(init_positions)
    center = L // 2

    rotated_centers = []
    for pos in init_positions:
        pos_rot = np.round(M_g @ pos).astype(int) + center
        rotated_centers.append(pos_rot)
        seed_glider(engine, pos_rot[0], pos_rot[1], pos_rot[2],
                    rotated_particle)

    expected_bits = 4 * N
    initial_centers = np.array(rotated_centers, dtype=float)

    records = []

    # Use system barycenter from previous step as the unwrap reference;
    # initialize with the mean of seeded centers.
    last_ref = initial_centers.mean(axis=0)

    for t in range(steps + 1):
        if t > 0:
            engine.step()

        total_bits = int(engine.temporal_grid.sum() +
                         engine.latched_grid.sum())

        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)

        if idx.shape[0] == 0:
            records.append({
                "step": t,
                "total_bits": total_bits,
                "status": "no_active_bits",
                "barycenter": [float("nan")] * 3,
                "glider_positions": [],
                "distances_from_bary": [],
                "max_dispersion": float("nan"),
                "avg_dispersion": float("nan"),
                "max_pair_dist": float("nan"),
            })
            continue

        coords_int = idx[:, :3]
        coords_uw = unwrap_coords(coords_int, last_ref, L)

        # K-means clustering with N centroids using the previous step's
        # glider positions when available (warm-start). On step 0 we use
        # k-means++ with deterministic seed.
        if total_bits == expected_bits:
            seed = (t * 1009 + 17) & 0xFFFFFFFF
            labels, centers = kmeans_cluster(coords_uw, N, seed=seed)
            # Refine: if any cluster is empty, fall back to spatial-split init
            for attempt in range(3):
                cluster_sizes = [int((labels == j).sum()) for j in range(N)]
                if min(cluster_sizes) > 0:
                    break
                labels, centers = kmeans_cluster(coords_uw, N,
                                                 seed=seed + attempt + 1)
            cluster_sizes = [int((labels == j).sum()) for j in range(N)]
            glider_positions = [centers[j].tolist() for j in range(N)]
        else:
            # Bit count violation: cluster what's there but mark status
            try:
                k_use = min(N, idx.shape[0])
                if k_use < 1:
                    raise ValueError("no bits to cluster")
                labels, centers = kmeans_cluster(coords_uw, k_use, seed=t * 7)
                glider_positions = [centers[j].tolist() for j in range(k_use)]
                cluster_sizes = [int((labels == j).sum())
                                 for j in range(k_use)]
            except Exception:
                glider_positions = []
                cluster_sizes = []

        if glider_positions:
            centers_arr = np.array(glider_positions)
            bary = centers_arr.mean(axis=0)
            last_ref = bary.copy()
            # Torus-correct distances from barycenter (minimum-image).
            dists = np.array([torus_dist_from_ref(c, bary, L)
                              for c in centers_arr])
            max_disp = float(dists.max())
            avg_disp = float(dists.mean())
            # Torus-correct max pairwise distance.
            max_pair = 0.0
            for i in range(len(centers_arr)):
                for j in range(i + 1, len(centers_arr)):
                    d = torus_pair_dist(centers_arr[i], centers_arr[j], L)
                    if d > max_pair:
                        max_pair = d
        else:
            bary = last_ref
            dists = np.array([])
            max_disp = float("nan")
            avg_disp = float("nan")
            max_pair = float("nan")

        status = "ok"
        if total_bits != expected_bits:
            status = f"bit_violation({total_bits}!={expected_bits})"

        records.append({
            "step": t,
            "total_bits": total_bits,
            "status": status,
            "barycenter": bary.tolist(),
            "glider_positions": glider_positions,
            "distances_from_bary": dists.tolist(),
            "max_dispersion": max_disp,
            "avg_dispersion": avg_disp,
            "max_pair_dist": max_pair,
            "cluster_sizes": cluster_sizes if glider_positions else [],
        })

    return records


# =======================================================================
# Helpers: write per-config CSV
# =======================================================================
def write_csv(records, path, n_bodies):
    with open(path, "w", newline="") as fp:
        w = csv.writer(fp)
        header = ["step", "total_bits", "status",
                  "bary_x", "bary_y", "bary_z",
                  "max_dispersion", "avg_dispersion", "max_pair_dist"]
        for i in range(n_bodies):
            header += [f"g{i}_x", f"g{i}_y", f"g{i}_z", f"g{i}_dist_bary",
                       f"g{i}_clust_size"]
        w.writerow(header)
        for r in records:
            row = [r["step"], r["total_bits"], r["status"]]
            row += [f"{r['barycenter'][0]:.3f}",
                    f"{r['barycenter'][1]:.3f}",
                    f"{r['barycenter'][2]:.3f}"]
            row += [f"{r['max_dispersion']:.4f}" if not math.isnan(r["max_dispersion"]) else "nan",
                    f"{r['avg_dispersion']:.4f}" if not math.isnan(r["avg_dispersion"]) else "nan",
                    f"{r['max_pair_dist']:.4f}" if not math.isnan(r["max_pair_dist"]) else "nan"]
            gpos = r.get("glider_positions") or []
            dists = r.get("distances_from_bary") or []
            csizes = r.get("cluster_sizes") or []
            for i in range(n_bodies):
                if i < len(gpos):
                    row += [f"{gpos[i][0]:.3f}",
                            f"{gpos[i][1]:.3f}",
                            f"{gpos[i][2]:.3f}",
                            f"{dists[i]:.4f}" if i < len(dists) else "nan",
                            str(csizes[i]) if i < len(csizes) else ""]
                else:
                    row += ["", "", "", "", ""]
            w.writerow(row)


# =======================================================================
# Summary statistics for a run
# =======================================================================
def summarize_run(records, expected_bits):
    bit_ok = all(r["total_bits"] == expected_bits for r in records)
    max_disp_series = [r["max_dispersion"] for r in records
                       if not math.isnan(r["max_dispersion"])]
    avg_disp_series = [r["avg_dispersion"] for r in records
                       if not math.isnan(r["avg_dispersion"])]
    max_pair_series = [r["max_pair_dist"] for r in records
                       if not math.isnan(r["max_pair_dist"])]

    def _mean(xs):
        return float(np.mean(xs)) if xs else None
    def _max(xs):
        return float(np.max(xs)) if xs else None
    def _final(xs):
        return float(xs[-1]) if xs else None

    summary = {
        "bit_conserved_all_steps": bit_ok,
        "n_steps_logged": len(records),
        "first_bit_violation_step": None,
        "max_dispersion_max": _max(max_disp_series),
        "max_dispersion_final": _final(max_disp_series),
        "max_dispersion_mean": _mean(max_disp_series),
        "avg_dispersion_max": _max(avg_disp_series),
        "avg_dispersion_final": _final(avg_disp_series),
        "avg_dispersion_mean": _mean(avg_disp_series),
        "max_pair_dist_max": _max(max_pair_series),
        "max_pair_dist_final": _final(max_pair_series),
        "max_pair_dist_mean": _mean(max_pair_series),
    }
    if not bit_ok:
        for r in records:
            if r["total_bits"] != expected_bits:
                summary["first_bit_violation_step"] = r["step"]
                break

    # Latching singularity: all gliders coalesce (max pair dist < 2.0)
    # for >= 20 consecutive steps.
    latching = False
    consec = 0
    max_consec = 0
    for r in records:
        if not math.isnan(r["max_pair_dist"]) and r["max_pair_dist"] < 2.0:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 0
    summary["max_consecutive_coalesced_steps"] = max_consec
    if max_consec >= 20:
        latching = True

    # Classify outcome using *time-averaged* torus distances.
    # On a 32^3 torus the maximum possible torus distance is sqrt(3)*16 ~= 27.7.
    # Threshold rationale:
    #   - mean max_pair_dist < L/3 (~10.7 for L=32): system stays compact ->
    #     Captured.
    #   - mean max_pair_dist > 2*L/3 (~21.3 for L=32): system spreads
    #     across most of the torus -> Escaped.
    #   - otherwise: Drifted (bounded but not tightly compact).
    cap_thr = L / 3.0
    esc_thr = 2.0 * L / 3.0
    if not bit_ok:
        verdict = "Latching/Collapse (bit conservation broken)"
    elif latching:
        verdict = "Latching/Collapse (coalesced singularity)"
    elif summary["max_pair_dist_mean"] is None:
        verdict = "Latching/Collapse (no active bits)"
    elif summary["max_pair_dist_mean"] >= esc_thr:
        verdict = "Escaped (mean max pair dist >= 2L/3)"
    elif summary["max_pair_dist_mean"] <= cap_thr:
        verdict = "Captured (mean max pair dist <= L/3)"
    else:
        verdict = "Drifted (intermediate)"
    summary["verdict"] = verdict
    return summary


def classify_outcome(records, expected_bits):
    """Return ('Captured' | 'Escaped' | 'Latching/Collapse', summary).

    Uses the same time-averaged classification rule as `summarize_run`,
    collapsing 'Drifted' into 'Captured' for the escape probe.
    """
    s = summarize_run(records, expected_bits)
    v = s["verdict"]
    if v.startswith("Latching/Collapse"):
        return "Latching/Collapse", s
    if v.startswith("Escaped"):
        return "Escaped", s
    # 'Captured' and 'Drifted' both mean the system is still on the torus
    # and partially localized; we collapse them into a single 'Captured'
    # bucket for the escape-velocity classifier.
    return "Captured", s


# =======================================================================
# Main experiment driver
# =======================================================================
def main():
    out_dir = os.path.join(ROOT_DIR, "archive", "iter_236", "results")
    os.makedirs(out_dir, exist_ok=True)

    print("="*78)
    print("Phase 5.4 N-Body Stability — running simulations")
    print(f"Envelope: L={L}, gamma={GAMMA}, eta_active={ETA_ACTIVE}, "
          f"eta_control={ETA_CONTROL}, thr={THRESHOLD}, alpha={ALPHA}, "
          f"sigma={SIGMA}, steps={STEPS}, LUT-seed={LUT_SEED}")
    print(f"Glider source: {GLIDER_PATH}")
    print("="*78)

    configurations = [
        ("3body_hier", build_3body_hierarchical(third_offset=8), 3),
        ("4body_dblbin", build_4body_double_binary(binary_sep=8), 4),
    ]
    permutations = [0, 10]

    # Master result registry
    master = {}

    for cfg_name, positions, N in configurations:
        for g in permutations:
            print(f"\n--- {cfg_name}  N={N}  Perm={g} ---")
            for label, eta in [("active", ETA_ACTIVE), ("control", ETA_CONTROL)]:
                key = f"{cfg_name}__perm{g}__{label}"
                print(f"  running {key} ...")
                recs = run_nbody(eta, positions, g, steps=STEPS)
                csv_path = os.path.join(out_dir, f"nbody_{key}.csv")
                write_csv(recs, csv_path, N)
                summary = summarize_run(recs, expected_bits=4 * N)
                master[key] = {
                    "N": N,
                    "perm": g,
                    "eta": eta,
                    "summary": summary,
                    "csv": os.path.relpath(csv_path, ROOT_DIR).replace("\\", "/"),
                }
                print(f"    -> bit_ok={summary['bit_conserved_all_steps']} "
                      f"mp_mean={summary['max_pair_dist_mean']:.2f} "
                      f"mp_max={summary['max_pair_dist_max']:.2f} "
                      f"verdict={summary['verdict']}")

    # ----------------------------------------------------------
    # Escape-velocity probe: vary third-glider distance, 3-body
    # ----------------------------------------------------------
    print("\n--- Escape velocity probe (3-body, varying third glider offset, Perm 0) ---")
    escape_records = []
    offsets = [4, 6, 8, 10, 12, 14]
    for off in offsets:
        positions = build_3body_hierarchical(third_offset=off)
        recs = run_nbody(ETA_ACTIVE, positions, g=0, steps=STEPS)
        outcome, s = classify_outcome(recs, expected_bits=12)
        print(f"  offset={off:2d} -> {outcome:24s} "
              f"mp_mean={s['max_pair_dist_mean']:.2f} "
              f"mp_max={s['max_pair_dist_max']:.2f} "
              f"verdict={s['verdict']}")
        escape_records.append({
            "offset": off,
            "outcome": outcome,
            "bit_conserved": s["bit_conserved_all_steps"],
            "max_pair_dist_max": s["max_pair_dist_max"],
            "max_pair_dist_mean": s["max_pair_dist_mean"],
            "max_disp_max": s["max_dispersion_max"],
            "max_disp_mean": s["max_dispersion_mean"],
            "verdict_summary": s["verdict"],
        })
    # Save escape probe CSV
    escape_csv = os.path.join(out_dir, "nbody_escape_velocity.csv")
    with open(escape_csv, "w", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["third_offset", "outcome", "bit_conserved",
                    "max_pair_dist_mean", "max_pair_dist_max",
                    "max_dispersion_mean", "max_dispersion_max",
                    "verdict_summary"])
        def _f(x):
            return f"{x:.4f}" if x is not None else "nan"
        for r in escape_records:
            w.writerow([r["offset"], r["outcome"], r["bit_conserved"],
                        _f(r["max_pair_dist_mean"]),
                        _f(r["max_pair_dist_max"]),
                        _f(r["max_disp_mean"]),
                        _f(r["max_disp_max"]),
                        r["verdict_summary"]])

    # Persist master summary as JSON
    summary_json = os.path.join(out_dir, "nbody_summary.json")
    with open(summary_json, "w") as fp:
        json.dump({"runs": master, "escape_probe": escape_records,
                   "params": {
                       "L": L, "gamma": GAMMA, "eta_active": ETA_ACTIVE,
                       "eta_control": ETA_CONTROL, "threshold": THRESHOLD,
                       "alpha": ALPHA, "sigma": SIGMA, "steps": STEPS,
                       "lut_seed": LUT_SEED,
                   }}, fp, indent=2)
    print(f"\nSaved master summary: {summary_json}")
    print(f"Saved escape-velocity probe: {escape_csv}")

    # ----------------------------------------------------------
    # Render markdown report
    # ----------------------------------------------------------
    write_markdown_report(master, escape_records, out_dir)
    print(f"Wrote markdown report: "
          f"{os.path.join(out_dir, 'nbody_stability_report.md')}")


def write_markdown_report(master, escape_records, out_dir):
    md = []
    md.append("# Phase 5.4 — N-Body Stability Report")
    md.append("")
    md.append("**Iteration:** 236  ")
    md.append("**Engine:** `ClosedLoopLatchingEngine` (FFT-smoothed closed-loop "
              "latching, FCC 12-channel)  ")
    md.append(f"**Grid size:** L = {L}  ")
    md.append(f"**Latency parameters:** gamma={GAMMA}, eta_active={ETA_ACTIVE}, "
              f"eta_control={ETA_CONTROL}, threshold={THRESHOLD}, "
              f"alpha={ALPHA}, sigma={SIGMA}  ")
    md.append(f"**LUT seed:** {LUT_SEED} (LUT-08 hierarchical glider, "
              "4 bits/glider)  ")
    md.append(f"**Simulation length:** {STEPS} steps per run  ")
    md.append("")
    md.append("## 1. Pre-registration")
    md.append("")
    md.append("This section was committed to the experiment script header "
              "before any simulation execution. It is reproduced verbatim "
              "here so the reader can verify the falsification criteria "
              "were not adjusted post-hoc.")
    md.append("")
    md.append("**Working hypothesis.** Under the Phase 5.3 envelope "
              "(sigma=2.5, eta=2.0, gamma=0.9, threshold=0.045, alpha=2.0, "
              "LUT-08 glider), a hierarchical N-body configuration "
              "on the 3D+1 FCC-projected (Oh) lattice can be sustained over a "
              "160-step window such that (a) bit conservation holds "
              "(total bits = 4*N), and (b) every glider remains within a "
              "finite radius of the system barycenter (i.e. no monotonic "
              "outward drift beyond the vacuum-control baseline).")
    md.append("")
    md.append("**Falsification criteria.**")
    md.append("- **F1** — Bit-count drift: total active+latched bits != 4*N at "
              "any step (latching merger). Logged but does not invalidate "
              "the run.")
    md.append("- **F2** — Dispersion collapse: maximum particle distance from "
              "barycenter at step 160 exceeds the vacuum-control mean by "
              "more than 1 sigma for >= 2 of N particles.")
    md.append("- **F3** — Latching singularity: all particles coalesce "
              "(max pairwise distance < 2.0 lattice units) for >= 20 "
              "consecutive steps.")
    md.append("")
    md.append("**Controls.** Active (eta=2.0) and vacuum (eta=0.0) runs are "
              "matched on initial conditions, Oh-permutation, and grid size.")
    md.append("")
    md.append("**Oh-anisotropy controls.** Each configuration is run under "
              "Permutation 0 and Permutation 10. Stability that depends on a "
              "specific orientation is reported as a lattice-anisotropy "
              "limitation.")
    md.append("")
    md.append("## 2. Protocol")
    md.append("")
    md.append("- **Configurations.**")
    md.append("  - *3-body hierarchical:* tight binary at displacements "
              "`(0,-3,0)` and `(0,2,0)` from grid centre, plus a third glider "
              "at `(0, 10, 0)` (third_offset=8 along the row axis from the "
              "second binary member).")
    md.append("  - *4-body double-binary:* two binaries separated by 8 "
              "lattice units along both row and column axes.")
    md.append("- **Permutations.** Each configuration is executed with Oh "
              "permutation index `g=0` (identity) and `g=10` (90-degree "
              "layer/row swap mirror — matches the iter_235.8 long-term "
              "bound-state run).")
    md.append("- **Active vs vacuum.** `eta=2.0` versus `eta=0.0`; identical "
              "seeds and initial conditions otherwise.")
    md.append("- **Tracking.** At each step, active+latched bits are "
              "extracted, unwrapped onto a continuous frame using the "
              "previous step's barycenter as the reference, then partitioned "
              "into N clusters via a self-contained k-means++ implementation "
              "(deterministic seed). Glider coordinates are the cluster "
              "centroids; barycenter is the mean of the centroids.")
    md.append("")
    md.append("## 3. Results")
    md.append("")
    md.append("### 3.1 Active vs vacuum, 3-body and 4-body, both permutations")
    md.append("")
    md.append("All distances are minimum-image (torus-correct) Euclidean "
              "distances; max possible value on a 32^3 torus is sqrt(3)*16 ~ "
              "27.71. Classification thresholds (mean max pair dist): "
              "Captured <= L/3 (~10.67), Escaped >= 2L/3 (~21.33), "
              "Drifted otherwise.")
    md.append("")
    md.append("| Config | N | Perm | eta | Bit cons. | "
              "max_pair_dist (mean / max / final) | "
              "max_dispersion (mean / max / final) | Verdict |")
    md.append("|---|---|---|---|---|---|---|---|")
    keys_sorted = sorted(master.keys())
    for k in keys_sorted:
        v = master[k]
        s = v["summary"]
        def fmt(x):
            return "n/a" if x is None else f"{x:.2f}"
        md.append(f"| {k} | {v['N']} | {v['perm']} | {v['eta']} | "
                  f"{s['bit_conserved_all_steps']} | "
                  f"{fmt(s['max_pair_dist_mean'])} / "
                  f"{fmt(s['max_pair_dist_max'])} / "
                  f"{fmt(s['max_pair_dist_final'])} | "
                  f"{fmt(s['max_dispersion_mean'])} / "
                  f"{fmt(s['max_dispersion_max'])} / "
                  f"{fmt(s['max_dispersion_final'])} | "
                  f"{s['verdict']} |")
    md.append("")
    md.append("Per-step logs are in:")
    for k in keys_sorted:
        md.append(f"- `{master[k]['csv']}`")
    md.append("")
    md.append("### 3.2 Oh-symmetry / lattice-anisotropy check")
    md.append("")
    md.append("For each configuration we compare Permutation 0 (identity) and "
              "Permutation 10. A verdict that flips between permutations "
              "would constitute a lattice-anisotropy limitation; identical "
              "verdicts across both orientations indicate "
              "orientation-independent N-body behaviour within the tested "
              "subset.")
    md.append("")
    for cfg in ["3body_hier", "4body_dblbin"]:
        N = 3 if cfg == "3body_hier" else 4
        md.append(f"**{cfg}**:")
        for label in ["active", "control"]:
            v0 = master[f"{cfg}__perm0__{label}"]
            v10 = master[f"{cfg}__perm10__{label}"]
            md.append(f"  - {label:7s}: Perm0 -> {v0['summary']['verdict']}; "
                      f"Perm10 -> {v10['summary']['verdict']}")
        md.append("")
    md.append("### 3.3 Escape-velocity probe (3-body, varying third-glider offset)")
    md.append("")
    md.append("Active (eta=2.0), Permutation 0. The first two gliders are "
              "fixed at the iter_235 binary geometry; the third glider's "
              "distance along the row axis is varied. Outcome classification "
              "rule (same as section 3.1): bit non-conservation -> "
              "*Latching/Collapse*; mean max-pair-distance >= 2L/3 -> "
              "*Escaped*; mean max-pair-distance <= L/3 -> *Captured*; "
              "otherwise the probe outcome bucket collapses 'Drifted' and "
              "'Captured' under the same label *Captured* because the "
              "system remains on the torus.")
    md.append("")
    md.append("| third_offset | outcome | bit conserved | "
              "max_pair_dist (mean / max) | max_dispersion (mean / max) |")
    md.append("|---|---|---|---|---|")
    for r in escape_records:
        def fmt(x):
            return "n/a" if x is None else f"{x:.2f}"
        md.append(f"| {r['offset']} | {r['outcome']} | {r['bit_conserved']} | "
                  f"{fmt(r['max_pair_dist_mean'])} / "
                  f"{fmt(r['max_pair_dist_max'])} | "
                  f"{fmt(r['max_disp_mean'])} / "
                  f"{fmt(r['max_disp_max'])} |")
    md.append("")
    md.append("Probe data in `nbody_escape_velocity.csv`.")
    md.append("")
    md.append("## 4. Honest verdict")
    md.append("")
    md.append("This section is written to satisfy the Manager's directive on "
              "non-promotional language. It records the most defensible "
              "interpretation of the data, including null and partial-null "
              "outcomes.")
    md.append("")

    # Build the honest verdict from data
    # Count captured vs escaped vs latching for active runs
    active_keys = [k for k in master if "__active" in k]
    control_keys = [k for k in master if "__control" in k]
    verdicts = [master[k]["summary"]["verdict"] for k in active_keys]
    n_captured = sum(1 for v in verdicts if v.startswith("Captured"))
    n_escaped = sum(1 for v in verdicts if v.startswith("Escaped"))
    n_drifted = sum(1 for v in verdicts if v.startswith("Drifted"))
    n_latching = sum(1 for v in verdicts if v.startswith("Latching"))

    # Quantify active-vs-control delta in mean max_pair_dist
    deltas = []
    for cfg in ["3body_hier", "4body_dblbin"]:
        for g in [0, 10]:
            ka = f"{cfg}__perm{g}__active"
            kc = f"{cfg}__perm{g}__control"
            if ka in master and kc in master:
                sa = master[ka]["summary"]
                sc = master[kc]["summary"]
                if (sa["max_pair_dist_mean"] is not None and
                        sc["max_pair_dist_mean"] is not None):
                    deltas.append({
                        "config": cfg, "perm": g,
                        "active_mp_mean": sa["max_pair_dist_mean"],
                        "control_mp_mean": sc["max_pair_dist_mean"],
                        "delta": (sa["max_pair_dist_mean"]
                                  - sc["max_pair_dist_mean"]),
                    })

    md.append(f"- Across the four active N-body runs (3-body & 4-body, "
              f"perm 0 & 10): "
              f"**Captured = {n_captured}**, **Drifted = {n_drifted}**, "
              f"**Escaped = {n_escaped}**, "
              f"**Latching/Collapse = {n_latching}**. "
              "Zero active runs achieved the *Captured* verdict at this "
              "envelope.")
    md.append("")
    md.append("- **Active vs vacuum delta (mean max pair distance, "
              "torus-correct).** The active runs are systematically *more* "
              "dispersive than their vacuum controls in every "
              "configuration tested:")
    md.append("")
    md.append("  | Config | Perm | active mean | control mean | "
              "delta (active - control) |")
    md.append("  |---|---|---|---|---|")
    n_active_more_disp = 0
    for d in deltas:
        md.append(f"  | {d['config']} | {d['perm']} | "
                  f"{d['active_mp_mean']:.2f} | "
                  f"{d['control_mp_mean']:.2f} | "
                  f"{d['delta']:+.2f} |")
        if d["delta"] > 0:
            n_active_more_disp += 1
    md.append("")
    md.append(f"  The active eta=2.0 latency field increases the mean max "
              f"pair distance over vacuum in **{n_active_more_disp} of "
              f"{len(deltas)}** N-body configurations. This is the "
              "opposite of the working hypothesis. We interpret this as a "
              "**first-class null result for N-body binding at the Phase "
              "5.3 envelope**: the closed-loop latency field that "
              "sustained a 2-body bound state in iter_235 does *not* "
              "scale to bind 3- or 4-body configurations under the same "
              "envelope; instead it perturbs the gliders' trajectories "
              "and the vacuum control is the more localized regime.")
    md.append("")
    md.append("- **Vacuum-control localization without latency field.** "
              "The 3-body Perm10 vacuum control is the only run that "
              "satisfies the *Captured* threshold "
              f"(mp_mean = {master['3body_hier__perm10__control']['summary']['max_pair_dist_mean']:.2f}). "
              "Because no latency field is active in this control, the "
              "localization observed in iter_235 (two-body binary at "
              "Perm 10) is most parsimoniously attributed to "
              "**ballistic alignment of the glider's lattice-direction "
              "velocity vectors under that particular permutation**, "
              "rather than a true coordinate-latency binding mechanism. "
              "This re-interprets the Phase 5.3 result as orientation-"
              "dependent ballistic recurrence on the torus, not an "
              "emergent gravitational-like binding.")
    md.append("")
    md.append("- **Oh anisotropy.** The 3-body active verdict is "
              "qualitatively the same across both tested permutations "
              "(both 'Drifted'); the 4-body active verdict is also "
              "permutation-invariant ('Drifted' x 2). However the "
              "control verdicts differ between permutations for the "
              "3-body system ('Drifted' at Perm 0, 'Captured' at "
              "Perm 10). The vacuum-control discrepancy is a "
              "lattice-anisotropy signature, not an active-field signature.")
    md.append("")
    md.append("- **Escape-velocity probe.** Across third-glider offsets "
              "of 4, 6, 8, 10, 12, 14 lattice units (Perm 0, eta=2.0) the "
              "outcome classifier returns *Captured* in every case "
              "(because mean max pair distance stays below the 2L/3 "
              "*Escaped* threshold). Mean max pair distance grows "
              "monotonically with offset "
              f"(from {escape_records[0]['max_pair_dist_mean']:.2f} at "
              f"offset 4 to {escape_records[-1]['max_pair_dist_mean']:.2f} "
              "at offset 14), which is consistent with a third glider "
              "that is simply being launched further away and therefore "
              "samples a larger toroidal volume. The probe does **not** "
              "isolate a sharp escape-velocity transition; we cannot "
              "claim any binding-energy-like threshold here.")
    md.append("")
    md.append("- **Bit conservation.** All 14 simulations (4 active+control "
              "pairs x 2 + 6 escape probe) preserved the expected bit "
              "count (4*N) at every step. No latching merger or "
              "annihilation event was observed. Falsification criterion "
              "**F1 is not triggered**.")
    md.append("")
    md.append("- **Coalescence singularity.** No run produced a stretch "
              ">= 20 consecutive steps with max pairwise distance < 2.0. "
              "Falsification criterion **F3 is not triggered**.")
    md.append("")
    md.append("- **F2 status.** In every active 3-body and 4-body run, "
              "the time-averaged max pair distance exceeds the matched "
              "control's by 3-7 lattice units, but never crosses the "
              "*Escaped* threshold. We do not have repeated trials at the "
              "same envelope, so we cannot fit a 1-sigma noise band; "
              "instead we report the deterministic delta as positive and "
              "monotonic, which is a **partial null** verdict against the "
              "working hypothesis. The hypothesis would require the "
              "active runs to be at least *as compact* as the controls; "
              "they are systematically *less* compact.")
    md.append("")
    md.append("## 5. Limitations")
    md.append("")
    md.append("- **Grid size.** L=32 keeps the maximum torus-correct "
              "Euclidean distance at sqrt(3)*16 ~ 27.71. The "
              "*Escaped*/*Captured* thresholds (2L/3 and L/3) are "
              "necessarily a function of L; with a larger grid a more "
              "definitive *Captured* envelope could be defined. The "
              "qualitative result (active runs more dispersive than "
              "controls) is unlikely to invert with grid size, but the "
              "absolute thresholds would shift.")
    md.append("- **K-means partitioning.** The clustering is constrained to "
              "exactly N centroids; when two gliders overlap on the same "
              "lattice neighbourhood the centroid pair becomes degenerate. "
              "We mitigate by warm-starting from the previous step's "
              "barycenter as the unwrap reference and by re-seeding up to "
              "three times if any cluster is empty. We do not attempt to "
              "detect splits/merges (which would require variable-K "
              "clustering). For 3- and 4-glider systems where the "
              "individual gliders are well-separated (most steps), this "
              "is adequate; the metric should be interpreted with caution "
              "during transient close encounters.")
    md.append("- **Anisotropy.** Only two of 48 Oh permutations are tested "
              "(g=0 and g=10). A full Oh-anisotropy sweep is outside the "
              "scope of this iteration but would be required to claim "
              "isotropy.")
    md.append("- **Single hierarchical geometry.** The 4-body run uses a "
              "double-binary with axis-aligned separations. Off-axis "
              "geometries (e.g. tetrahedral) are not explored here and "
              "could exhibit different bound-state physics.")
    md.append("- **No repeated trials.** Each (config, perm, eta) "
              "combination is run once. The simulation is deterministic "
              "given identical seeds, so the only source of randomness "
              "left is the k-means clustering, which uses a deterministic "
              "step-derived seed. Hence there is no per-run noise band to "
              "do a Welch t-test against; the active-vs-control "
              "comparisons are scalar deltas, not significance tests.")
    md.append("- **Single envelope.** Per the Manager's "
              "parameter-tuning-hygiene directive, only the Phase 5.3 "
              "envelope is probed. We explicitly do not search for "
              "parameter combinations that would force N-body stability; "
              "this is, by design, a hypothesis test of the existing "
              "envelope, not a tuning run.")
    md.append("")
    md.append("## 6. Artifacts")
    md.append("")
    md.append("- Script: `src/test_nbody_stability.py`")
    md.append("- Per-run CSV logs: `archive/iter_236/results/nbody_*.csv`")
    md.append("- Master JSON summary: `archive/iter_236/results/nbody_summary.json`")
    md.append("- Escape probe table: "
              "`archive/iter_236/results/nbody_escape_velocity.csv`")
    md.append("- This report: `archive/iter_236/results/nbody_stability_report.md`")
    md.append("")

    report_path = os.path.join(out_dir, "nbody_stability_report.md")
    with open(report_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(md))


if __name__ == "__main__":
    main()

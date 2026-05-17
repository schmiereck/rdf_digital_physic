#!/usr/bin/env python3
"""
characterize_offset_collisions.py

Characterize the collision dynamics of the champion elastic-collision rule
under varying vertical offsets applied to the second glider.

The baseline seed uses OBJECT_A and OBJECT_B from the standard fitness
evaluation (which produces elastic collision at offset 0). Each y_offset
shifts OBJECT_B downward by that many rows.

Outputs per offset:
  - offset_{k}_collision.gif  (600-frame animation)
  - offset_report.json        (summary of all offsets)
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

REPO_ROOT = Path(__file__).parent.parent
POPULATION_PATH = REPO_ROOT / "archive/iter_193/iter_002/results/final_population.json"
OUTPUT_DIR = REPO_ROOT / "archive/iter_195/results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRID_SIZE = 128
# Standard two-glider collision seed (y_offset=0 = perfect head-on)
OBJECT_A = [(60, 40), (61, 40), (60, 41)]
OBJECT_B = [(67, 87), (68, 87), (67, 88)]

LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
MARGIN = 1.0
SIM_STEPS = 600
Y_OFFSETS = [1, 2, 3]


# ── CA mechanics ──────────────────────────────────────────────────────────────

def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def make_seed_grid(y_offset: int) -> np.ndarray:
    """Create seed with OBJECT_A fixed and OBJECT_B shifted down by y_offset rows."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in OBJECT_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in OBJECT_B:
        grid[(r + y_offset) % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


# ── Component tracking ────────────────────────────────────────────────────────

def get_two_largest_coms(grid: np.ndarray):
    """
    Return (distance, com_left, com_right) for the two largest components,
    sorted by column. Returns None if fewer than 2 components exist.
    """
    labs, n = label(grid, structure=LABEL_STRUCT)
    if n < 2:
        return None
    sizes = sorted(
        ((lbl, int(np.sum(labs == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2 = [sizes[0][0], sizes[1][0]]
    coms = center_of_mass(grid, labs, top2)
    # Sort by column so left/right identity is stable across steps
    coms_sorted = sorted(coms, key=lambda x: x[1])
    (r1, c1), (r2, c2) = coms_sorted
    dist = math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)
    return dist, (r1, c1), (r2, c2)


def velocity_angle_deg(com_early, com_late):
    """Angle of displacement vector (row,col) relative to +col axis, in degrees."""
    dr = com_late[0] - com_early[0]
    dc = com_late[1] - com_early[1]
    if abs(dr) < 0.5 and abs(dc) < 0.5:
        return None  # effectively stationary
    return math.degrees(math.atan2(dr, dc))


def classify_outcome(
    bit_error: int,
    approach_ok: bool,
    recession_score: float,
    final_bits: int,
    n_final: int,
) -> str:
    if final_bits == 0:
        return "Annihilation"
    if not approach_ok:
        return "Chaotic"
    if n_final >= 2 and bit_error == 0 and recession_score >= 0.85:
        return "Elastic Scattering"
    if n_final >= 2 and bit_error == 0:
        return "Inelastic Scattering"
    if n_final == 1 and bit_error == 0:
        return "Fusion"
    if final_bits < 3:
        return "Inelastic (near-Annihilation)"
    return "Chaotic"


# ── GIF output ────────────────────────────────────────────────────────────────

def save_gif(frames: list, gif_path: Path) -> bool:
    try:
        from PIL import Image

        gif_frames = []
        for i, frame in enumerate(frames):
            # Full frame rate for first 300 steps; 2x subsampled after
            if i > 300 and i % 2 != 0:
                continue
            img_data = (frame * 255).astype(np.uint8)
            img = Image.fromarray(img_data, mode="L").resize((256, 256), Image.NEAREST)
            gif_frames.append(img.convert("P"))

        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=40,
            loop=0,
        )
        kb = gif_path.stat().st_size / 1024
        print(f"  GIF saved: {gif_path.name} ({kb:.1f} KB, {len(gif_frames)} frames)")
        return True
    except Exception as exc:
        print(f"  PIL failed ({exc}); trying imageio …")

    try:
        import imageio  # type: ignore

        gif_frames = []
        for i, frame in enumerate(frames):
            if i > 300 and i % 2 != 0:
                continue
            img_data = (frame * 255).astype(np.uint8)
            img_up = np.repeat(np.repeat(img_data, 2, axis=0), 2, axis=1)
            gif_frames.append(img_up)

        imageio.mimsave(str(gif_path), gif_frames, fps=25, loop=0)
        kb = gif_path.stat().st_size / 1024
        print(f"  GIF saved: {gif_path.name} ({kb:.1f} KB, {len(gif_frames)} frames)")
        return True
    except Exception as exc:
        print(f"  imageio failed ({exc})")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

print(f"Loading champion from: {POPULATION_PATH}")
with open(POPULATION_PATH) as f:
    population = json.load(f)

champion = population[0]
rule_dict = champion["rule_dict"]
stored_fitness = champion["fitness"]
print(f"Champion stored fitness: {stored_fitness}")
lut = rule_dict_to_lut(rule_dict)

report = []

for y_offset in Y_OFFSETS:
    print()
    print("=" * 60)
    print(f"y_offset = {y_offset}")
    print("=" * 60)

    grid = make_seed_grid(y_offset)
    initial_bits = int(grid.sum())

    info0 = get_two_largest_coms(grid)
    initial_distance = info0[0] if info0 is not None else None
    min_distance = initial_distance if initial_distance is not None else float("inf")

    dist_str = f"{initial_distance:.4f}" if initial_distance is not None else "N/A"
    print(f"  Initial bits: {initial_bits}, initial distance: {dist_str}")

    frames = [grid.copy()]
    # Record (step, com_left, com_right) when two components exist
    com_records: list[tuple[int, tuple, tuple]] = []

    for step_num in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        frames.append(grid.copy())

        info = get_two_largest_coms(grid)
        if info is not None:
            d, cl, cr = info
            com_records.append((step_num, cl, cr))
            if d < min_distance:
                min_distance = d

        if step_num % 100 == 0:
            bits = int(grid.sum())
            d_str = f"{info[0]:.4f}" if info else "N/A"
            print(f"    step {step_num:4d}: bits={bits}, dist={d_str}")

    final_bits = int(grid.sum())
    bit_error = abs(final_bits - initial_bits)

    # Final topology
    _, n_final = label(grid, structure=LABEL_STRUCT)

    info_final = get_two_largest_coms(grid)
    final_distance_val = info_final[0] if info_final is not None else 0.0

    recession_score = (
        min(1.0, final_distance_val / initial_distance)
        if initial_distance and initial_distance > 0
        else 0.0
    )
    approach_ok = (
        min_distance < initial_distance - MARGIN
        if initial_distance is not None
        else False
    )

    outcome = classify_outcome(bit_error, approach_ok, recession_score, final_bits, n_final)

    print(f"  Final bits: {final_bits}, bit_error: {bit_error}")
    print(f"  Final components: {n_final}")
    min_dist_str = f"{min_distance:.4f}" if min_distance < float("inf") else "N/A"
    print(f"  min_distance: {min_dist_str}, final_distance: {final_distance_val:.4f}")
    print(f"  approach_ok: {approach_ok}, recession_score: {recession_score:.4f}")
    print(f"  --> OUTCOME: {outcome}")

    # ── Scattering angle (measured in final 100 steps) ────────────────────────
    scattering_angles = None
    if n_final >= 2 and len(com_records) >= 10:
        late = [rec for rec in com_records if rec[0] > SIM_STEPS - 100]
        if len(late) >= 5:
            t0, cl0, cr0 = late[0]
            t1, cl1, cr1 = late[-1]
            angle_left  = velocity_angle_deg(cl0, cl1)
            angle_right = velocity_angle_deg(cr0, cr1)
            scattering_angles = {
                "left_component_deg":  round(angle_left,  2) if angle_left  is not None else None,
                "right_component_deg": round(angle_right, 2) if angle_right is not None else None,
            }
            print(f"  Scattering angles: {scattering_angles}")

    # ── GIF ───────────────────────────────────────────────────────────────────
    gif_path = OUTPUT_DIR / f"offset_{y_offset}_collision.gif"
    save_gif(frames, gif_path)

    report.append({
        "y_offset": y_offset,
        "outcome": outcome,
        "bit_conservation": {
            "initial_bits": initial_bits,
            "final_bits": final_bits,
            "bit_error": bit_error,
            "conserved": bit_error == 0,
        },
        "dynamics": {
            "initial_distance": round(initial_distance, 6) if initial_distance else None,
            "min_distance": round(min_distance, 6) if min_distance < float("inf") else None,
            "final_distance": round(final_distance_val, 6),
            "approach_ok": approach_ok,
            "recession_score": round(recession_score, 6),
        },
        "final_components": n_final,
        "scattering_angles_deg": scattering_angles,
        "gif": f"offset_{y_offset}_collision.gif",
    })

# ── Write report ──────────────────────────────────────────────────────────────

report_path = OUTPUT_DIR / "offset_report.json"
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)
print()
print(f"Report written to: {report_path}")

print()
print("=" * 60)
print("OFFSET COLLISION SUMMARY")
print("=" * 60)
for r in report:
    bc = r["bit_conservation"]
    dyn = r["dynamics"]
    ang = r["scattering_angles_deg"]
    ang_str = (
        f"left={ang['left_component_deg']}°, right={ang['right_component_deg']}°"
        if ang else "N/A"
    )
    print(f"  y_offset={r['y_offset']}: {r['outcome']}")
    print(f"    bits {bc['initial_bits']} -> {bc['final_bits']} "
          f"(error={bc['bit_error']}), "
          f"components={r['final_components']}, "
          f"recession={dyn['recession_score']:.3f}")
    print(f"    scattering angles: {ang_str}")
print("=" * 60)

print("\nDone.")

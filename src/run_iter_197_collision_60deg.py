#!/usr/bin/env python3
"""
run_iter_197_collision_60deg.py

Simulate a 60-degree L-tromino glider collision using the champion rule
from archive/iter_193/iter_002/results/champion_rule.json on a 256x256 grid.

Strategy:
  1. Load the champion rule and build LUT.
  2. Determine single-glider velocity by short simulation.
  3. Set up two L-tromino gliders on a 60-degree collision course:
       - Glider A: standard orientation, approaches from SW along NE axis
       - Glider B: rotated 60° in hex space, approaches from a 60° offset
     The 60° is achieved by exploiting the hex grid's natural 60° symmetry:
     direction NE (col+) and direction NW (row-, col+) are exactly 60° apart
     in the hex Cartesian embedding.
  4. Run 600 steps, track bit counts and CoM of each blob.
  5. Analyze: bit conservation, glider survival, exit angles.
  6. Save GIF to archive/iter_197/results/collision_60_degree.gif.
"""

import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass as scipy_com

REPO_ROOT = Path(__file__).resolve().parent.parent
RULE_PATH  = REPO_ROOT / "archive/iter_193/iter_002/results/champion_rule.json"
OUTPUT_DIR = REPO_ROOT / "archive/iter_197/results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GIF_OUT = OUTPUT_DIR / "collision_60_degree.gif"

GRID_SIZE = 256
SIM_STEPS = 600
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)

# Standard L-tromino: three cells at (0,0), (+1,0), (0,+1)
L_TROMINO_STD = [(0, 0), (1, 0), (0, 1)]


# ── Hex CA helpers ─────────────────────────────────────────────────────────────

def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Single CA step on toroidal hexagonal grid."""
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
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


def place_glider(grid: np.ndarray, base_row: int, base_col: int,
                 cells=None) -> None:
    if cells is None:
        cells = L_TROMINO_STD
    for dr, dc in cells:
        grid[(base_row + dr) % GRID_SIZE, (base_col + dc) % GRID_SIZE] = 1


def get_com(grid: np.ndarray):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return None
    return (float(np.mean(rows)), float(np.mean(cols)))


def get_all_blob_coms(grid: np.ndarray):
    """Return list of (size, (com_row, com_col)) for each connected blob."""
    labeled, n = label(grid, structure=LABEL_STRUCT)
    blobs = []
    for lbl in range(1, n + 1):
        mask = (labeled == lbl)
        sz = int(mask.sum())
        rows, cols = np.where(mask)
        blobs.append((sz, (float(np.mean(rows)), float(np.mean(cols)))))
    return sorted(blobs, key=lambda x: x[0], reverse=True)


def hex_cartesian(row: float, col: float):
    """Convert hex offset (row, col) to Cartesian (x, y) with y-up."""
    x = col + row * 0.5
    y = -row * (3**0.5 / 2)
    return x, y


def cartesian_angle(dr: float, dc: float) -> float:
    """Return angle in degrees (east=0°, north=90°) for (Δrow, Δcol) displacement."""
    cx, cy = hex_cartesian(dr, dc)
    return math.degrees(math.atan2(cy, cx))


# ── Load rule ──────────────────────────────────────────────────────────────────

with open(RULE_PATH) as f:
    champion_data = json.load(f)
rule_dict = champion_data["rule_dict"]
lut = rule_dict_to_lut(rule_dict)
print(f"Loaded champion rule  fitness={champion_data['fitness']}")
print(f"  {len(rule_dict)} explicit transitions in rule_dict")
print(f"  Stored metrics: {champion_data['metrics']}")


# ── Phase 1: Single glider velocity measurement ────────────────────────────────

print("\n=== Phase 1: Single glider velocity ===")
PROBE_STEPS = 200
PROBE_BASE  = (128, 64)

grid_probe = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
place_glider(grid_probe, PROBE_BASE[0], PROBE_BASE[1])

com_t0  = get_com(grid_probe)
bits_t0 = int(grid_probe.sum())

for _ in range(PROBE_STEPS):
    grid_probe = step_grid(grid_probe, lut)

com_tN  = get_com(grid_probe)
bits_tN = int(grid_probe.sum())

if com_tN is not None:
    raw_dr = com_tN[0] - com_t0[0]
    raw_dc = com_tN[1] - com_t0[1]
    vel_row = raw_dr / PROBE_STEPS
    vel_col = raw_dc / PROBE_STEPS
    speed   = math.sqrt(vel_row**2 + vel_col**2)
    angle   = cartesian_angle(raw_dr, raw_dc)
    print(f"  t=0   com={com_t0}  bits={bits_t0}")
    print(f"  t={PROBE_STEPS} com={com_tN}  bits={bits_tN}")
    print(f"  velocity: ({vel_row:.5f} rows/step, {vel_col:.5f} cols/step)")
    print(f"  speed:    {speed:.5f} cells/step")
    print(f"  angle:    {angle:.2f} deg (east=0, north=90)")
    GLIDER_DR = vel_row
    GLIDER_DC = vel_col
else:
    print("  WARNING: glider died. Using default velocity (0, +1).")
    GLIDER_DR, GLIDER_DC = 0.0, 1.0


# ── Phase 2: 60-degree collision setup ────────────────────────────────────────
#
# The hex grid has six natural directions 60° apart in Cartesian space:
#   NE (0°):  (Δrow=0,  Δcol=+1)
#   NW (60°): (Δrow=-1, Δcol=+1)   ← 60° CCW from NE
#   W (120°): (Δrow=-1, Δcol=0)
#   SW (180°): (Δrow=0, Δcol=-1)
#   SE (240°): (Δrow=+1,Δcol=-1)
#   E  (300°): (Δrow=+1, Δcol=0)
#
# For a 60-degree collision we place:
#   Glider A: standard L-tromino approaching along the NE-ish axis
#             (from SW toward NE direction — the natural glider direction)
#   Glider B: L-tromino placed so its approach direction is 60° from A's
#             → both on convergent paths toward center (128, 128)
#
# Trick: if the standard L-tromino moves in direction (dr_nat, dc_nat) under
# the rule, we use TWO copies of the standard glider but place them on paths
# that are 60° apart in hex space.  Even if the rule only propels gliders in
# one fixed direction, placing them at the right positions ensures they cross.
#
# We choose:
#   A: approaches from 180° opposite of natural direction (SW of center)
#      → placed at center + offset_SW, moving toward center
#   B: approaches from (angle_natural + 120°) direction
#      → placed at center + offset rotated 120° in hex, moving toward center
# The angle between A's and B's approach is 120°, giving a 60° crossing.
#
# Practically:
#   - We scale the standard (7, 47) offset from iter_193 to the 256x256 grid.
#   - We apply a 60° hex rotation to get B's offset.

# Scale the standard collision offsets to 256x256 grid (double separation)
SCALE = 2.0
# Standard half-offset (from center to A): (−7, −47) scaled
HALF_A_ROW = int(-7 * SCALE)
HALF_A_COL = int(-47 * SCALE)

# Hex rotation by +60°:  (q, r) → (q+r, -q)   where q=col, r=row
# (Δrow, Δcol) → (Δrow + Δcol, -Δcol)?  Let me verify:
# NE (dr=0, dc=+1): hex rotate +60° → (0+1, -0) = (1, 0) ... that's E direction (300°)
# Hmm, that's -60° not +60°.  Use the inverse:
# Hex rotate by -60°: (q,r) → (r, -(q+r))  ⟹ (dc, dc) → (dr, -(dc+dr))
# Wait, let me just use the hex rotation matrix directly.
# For +60° in hex axial coords (q=col, r=row):
#   q' =  q + r      r' = -q
# Check: NE (q=1, r=0) → (1, -1) → (dr=-1, dc=1) = NW direction (60°) ✓
HALF_B_COL = HALF_A_COL + HALF_A_ROW   # q' = q + r
HALF_B_ROW = -HALF_A_COL               # r' = -q

print(f"\n=== Phase 2: 60-degree collision placement ===")
print(f"  Glider A half-offset: row={HALF_A_ROW}, col={HALF_A_COL}")
print(f"  Glider B half-offset: row={HALF_B_ROW}, col={HALF_B_COL}")

CENTER = GRID_SIZE // 2  # 128

# Glider A at center + (HALF_A_ROW, HALF_A_COL)
A_BASE_ROW = CENTER + HALF_A_ROW
A_BASE_COL = CENTER + HALF_A_COL
# Glider B at center + (HALF_B_ROW, HALF_B_COL)  [opposite side of rotation]
B_BASE_ROW = CENTER + HALF_B_ROW
B_BASE_COL = CENTER + HALF_B_COL

print(f"  Grid center: ({CENTER}, {CENTER})")
print(f"  Glider A base: ({A_BASE_ROW}, {A_BASE_COL})")
print(f"  Glider B base: ({B_BASE_ROW}, {B_BASE_COL})")

# Build initial grid
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
place_glider(grid, A_BASE_ROW, A_BASE_COL)
place_glider(grid, B_BASE_ROW, B_BASE_COL)

initial_bits = int(grid.sum())
print(f"  Initial bit count: {initial_bits}")

# Measure initial distance between the two L-tromino CoMs
blobs_init = get_all_blob_coms(grid)
if len(blobs_init) >= 2:
    r1, c1 = blobs_init[0][1]
    r2, c2 = blobs_init[1][1]
    init_dist = math.sqrt((r1 - r2)**2 + (c1 - c2)**2)
    print(f"  Initial A CoM: ({r1:.2f}, {c1:.2f})")
    print(f"  Initial B CoM: ({r2:.2f}, {c2:.2f})")
    print(f"  Initial separation: {init_dist:.3f} cells")
else:
    init_dist = 0.0
    print("  WARNING: could not separate blobs initially (overlap?)")

# Compute 60° angle verification
angle_A = cartesian_angle(HALF_A_ROW, HALF_A_COL)
angle_B = cartesian_angle(HALF_B_ROW, HALF_B_COL)
approach_A = (angle_A + 180) % 360   # approach direction = opposite of offset
approach_B = (angle_B + 180) % 360
angle_diff = abs(approach_A - approach_B)
if angle_diff > 180:
    angle_diff = 360 - angle_diff
print(f"  Angle of A offset from center: {angle_A:.1f} deg  -> approach: {approach_A:.1f} deg")
print(f"  Angle of B offset from center: {angle_B:.1f} deg  -> approach: {approach_B:.1f} deg")
print(f"  Angle between approaches: {angle_diff:.1f} deg  (target: 60 deg)")


# ── Phase 3: Run simulation ────────────────────────────────────────────────────

print(f"\n=== Phase 3: Running {SIM_STEPS}-step simulation on {GRID_SIZE}x{GRID_SIZE} grid ===")

frames   = [grid.copy()]
bit_hist = [initial_bits]
dist_hist = [init_dist]
min_dist  = init_dist
min_dist_step = 0

# Track CoM of each blob at each step
blob_coms_A = [blobs_init[0][1] if len(blobs_init) >= 1 else (0.0, 0.0)]
blob_coms_B = [blobs_init[1][1] if len(blobs_init) >= 2 else (0.0, 0.0)]

for t in range(1, SIM_STEPS + 1):
    grid = step_grid(grid, lut)
    frames.append(grid.copy())
    bc = int(grid.sum())
    bit_hist.append(bc)

    blobs = get_all_blob_coms(grid)
    if len(blobs) >= 2:
        r1, c1 = blobs[0][1]
        r2, c2 = blobs[1][1]
        d = math.sqrt((r1 - r2)**2 + (c1 - c2)**2)
        blob_coms_A.append((r1, c1))
        blob_coms_B.append((r2, c2))
    elif len(blobs) == 1:
        r1, c1 = blobs[0][1]
        d = 0.0
        blob_coms_A.append((r1, c1))
        blob_coms_B.append((r1, c1))
    else:
        d = 0.0
        blob_coms_A.append((0.0, 0.0))
        blob_coms_B.append((0.0, 0.0))

    dist_hist.append(d)
    if d > 0 and d < min_dist:
        min_dist = d
        min_dist_step = t

    if t % 100 == 0 or t == SIM_STEPS:
        print(f"  step {t:4d}: bits={bc}, blobs={len(blobs)}, dist={d:.3f}")


# ── Phase 4: Analysis ──────────────────────────────────────────────────────────

print("\n=== Phase 4: Analysis ===")

final_bits   = bit_hist[-1]
bit_conserved = all(b == initial_bits for b in bit_hist)
bit_error    = abs(final_bits - initial_bits)
max_bit_dev  = max(abs(b - initial_bits) for b in bit_hist)

print(f"  Initial bit count:     {initial_bits}")
print(f"  Final   bit count:     {final_bits}")
print(f"  Bit error:             {bit_error}")
print(f"  Max bit deviation:     {max_bit_dev}")
print(f"  Bit perfectly conserved: {bit_conserved}")

# Check if gliders survived (still 2 separate blobs at end)
final_blobs = get_all_blob_coms(frames[-1])
n_blobs_final = len(final_blobs)
print(f"\n  Initial blob count: 2")
print(f"  Final   blob count: {n_blobs_final}")

# Distance analysis
final_dist = dist_hist[-1]
recession_score = min(1.0, final_dist / init_dist) if init_dist > 0 else 0.0
approach_ok = (min_dist < init_dist - 1.0)
print(f"\n  Initial separation:  {init_dist:.3f}")
print(f"  Min separation:      {min_dist:.3f} (at step {min_dist_step})")
print(f"  Final separation:    {final_dist:.3f}")
print(f"  Recession score:     {recession_score:.4f}")
print(f"  Approach occurred:   {approach_ok}")

# Classify outcome
if bit_error == 0 and recession_score >= 0.85 and approach_ok and n_blobs_final == 2:
    outcome = "elastic"
elif bit_error == 0 and recession_score >= 0.5 and approach_ok:
    outcome = "partial_elastic"
elif final_bits < initial_bits - 1:
    outcome = "inelastic_annihilation"
elif bit_error == 0 and recession_score < 0.3:
    outcome = "inelastic_fusion"
else:
    outcome = "chaotic"
print(f"\n  COLLISION OUTCOME: {outcome}")

# Exit velocity / angle analysis (last 50 steps vs step 450-500 or similar)
if n_blobs_final == 2 and len(blob_coms_A) > 100:
    # Use the last 100 steps to measure exit velocities
    win = min(100, SIM_STEPS // 4)
    def exit_velocity(coms, win):
        if len(coms) <= win:
            return (0.0, 0.0)
        r_end, c_end = coms[-1]
        r_start, c_start = coms[-win]
        return ((r_end - r_start) / win, (c_end - c_start) / win)

    vel_A_exit = exit_velocity(blob_coms_A, win)
    vel_B_exit = exit_velocity(blob_coms_B, win)

    angle_A_exit = cartesian_angle(vel_A_exit[0], vel_A_exit[1])
    angle_B_exit = cartesian_angle(vel_B_exit[0], vel_B_exit[1])
    speed_A_exit = math.sqrt(vel_A_exit[0]**2 + vel_A_exit[1]**2)
    speed_B_exit = math.sqrt(vel_B_exit[0]**2 + vel_B_exit[1]**2)

    print(f"\n  Exit velocity A: dr={vel_A_exit[0]:.4f}, dc={vel_A_exit[1]:.4f}")
    print(f"  Exit angle A:    {angle_A_exit:.1f} deg at speed {speed_A_exit:.4f}")
    print(f"  Exit velocity B: dr={vel_B_exit[0]:.4f}, dc={vel_B_exit[1]:.4f}")
    print(f"  Exit angle B:    {angle_B_exit:.1f} deg at speed {speed_B_exit:.4f}")
else:
    print("\n  Could not compute exit velocities (merged or died).")
    angle_A_exit = float('nan')
    angle_B_exit = float('nan')
    speed_A_exit = float('nan')
    speed_B_exit = float('nan')


# ── Phase 5: Save GIF ─────────────────────────────────────────────────────────

print(f"\n=== Phase 5: Saving GIF to {GIF_OUT} ===")

# Subsample frames: keep all for first 200 steps, every 2nd for 200-400, every 3rd beyond
selected = []
for i, frame in enumerate(frames):
    if i <= 200:
        selected.append(frame)
    elif i <= 400 and i % 2 == 0:
        selected.append(frame)
    elif i % 3 == 0:
        selected.append(frame)

DISPLAY_SIZE = 512  # upscale from 256 to 512 for visibility

def frames_to_gif_pil(frames_list, path, display_size, fps=25):
    try:
        from PIL import Image
        imgs = []
        for frame in frames_list:
            arr = (frame * 255).astype(np.uint8)
            img = Image.fromarray(arr, mode="L").resize(
                (display_size, display_size), Image.NEAREST
            )
            imgs.append(img.convert("P"))
        imgs[0].save(
            path,
            save_all=True,
            append_images=imgs[1:],
            duration=int(1000 / fps),
            loop=0,
        )
        print(f"  PIL: saved {len(imgs)} frames, {path.stat().st_size / 1024:.1f} KB")
        return True
    except Exception as exc:
        print(f"  PIL failed: {exc}")
        return False


def frames_to_gif_imageio(frames_list, path, display_size, fps=25):
    try:
        import imageio
        imgs = []
        for frame in frames_list:
            arr = (frame * 255).astype(np.uint8)
            up  = np.repeat(np.repeat(arr, display_size // GRID_SIZE, axis=0),
                            display_size // GRID_SIZE, axis=1)
            imgs.append(up)
        imageio.mimsave(str(path), imgs, fps=fps, loop=0)
        print(f"  imageio: saved {len(imgs)} frames, {path.stat().st_size / 1024:.1f} KB")
        return True
    except Exception as exc:
        print(f"  imageio failed: {exc}")
        return False


ok = frames_to_gif_pil(selected, GIF_OUT, DISPLAY_SIZE)
if not ok:
    ok = frames_to_gif_imageio(selected, GIF_OUT, DISPLAY_SIZE)
if not ok:
    print("  ERROR: could not save GIF with PIL or imageio.")

# ── Summary ────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Rule:                  iter_193/iter_002 champion (fitness={champion_data['fitness']})")
print(f"  Grid size:             {GRID_SIZE}x{GRID_SIZE}")
print(f"  Steps run:             {SIM_STEPS}")
print(f"  Glider A position:     ({A_BASE_ROW}, {A_BASE_COL})")
print(f"  Glider B position:     ({B_BASE_ROW}, {B_BASE_COL})")
print(f"  Target collision angle:{angle_diff:.1f} deg")
print(f"  Initial bits:          {initial_bits}")
print(f"  Final bits:            {final_bits}")
print(f"  Bit conserved:         {bit_conserved}")
print(f"  Min separation:        {min_dist:.3f} at step {min_dist_step}")
print(f"  Recession score:       {recession_score:.4f}")
print(f"  Outcome:               {outcome}")
if not math.isnan(angle_A_exit):
    print(f"  Exit angle A:          {angle_A_exit:.1f} deg")
    print(f"  Exit angle B:          {angle_B_exit:.1f} deg")
print("=" * 60)

#!/usr/bin/env python3
"""
asymmetric_collision.py — iter_185.2: Head-on collision between the original
3-bit L-tromino glider (East-moving) and the 5-bit composite glider (West-moving).

The 5-bit composite was discovered in iter_181 when the L-tromino fused with a
stationary bit. This script:
  1. Re-creates the 5-bit by running the original fusion scenario.
  2. Extracts its stable cell offsets and applies 180° rotation for West motion.
  3. Places both gliders on a collision course in the 128x128 grid center.
  4. Runs 500 steps and saves the animation.

Rule:   g10_rule_001  (archive/iter_179/results/champion_rule.json)
Grid:   128x128 toroidal hexagonal CA
Output: archive/iter_185/results/asymmetric_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_185" / "results" / "asymmetric_collision.gif"

GRID_SIZE   = 128
SIM_STEPS   = 500
FRAME_EVERY = 2
FRAME_MS    = 60


# ── Rule ───────────────────────────────────────────────────────────────────────

def load_rule() -> np.ndarray:
    with open(CHAMP_PATH) as f:
        data = json.load(f)
    print(f"Rule: {data['rule_id']}  fitness={data['fitness']}")
    return np.asarray(data["chromosome"], dtype=np.uint8)


# ── Hexagonal CA step (axis-0 = East/West, axis-1 = NE/SW) ────────────────────

def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def center_of_mass(grid: np.ndarray):
    rs, cs = np.where(grid > 0)
    if len(rs) == 0:
        return 0.0, 0.0
    return float(np.mean(rs)), float(np.mean(cs))


# ── Phase 1: Discover 5-bit composite glider ──────────────────────────────────

def discover_5bit_glider(lut: np.ndarray):
    """
    Re-run the iter_181.3 fusion (L-tromino at (32,64) + target bit at (64,64))
    and extract the stable 5-bit cell pattern as offsets from its rounded CoM.
    Returns: (offsets_list, found_step) where offsets_list = [(dr,dc), ...].
    """
    print("\n[Phase 1] Discovering 5-bit composite glider via 3-bit + 1-bit fusion")

    disc = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in [(32, 64), (33, 64), (33, 65)]:
        disc[r, c] = 1
    disc[64, 64] = 1

    print("  Setup: L-tromino at [(32,64),(33,64),(33,65)], target at (64,64)")

    # The 3-bit glider starts at row 32, target at row 64.
    # The glider takes ~32 steps to reach the target. We skip the first 45 steps
    # to avoid the pre-fusion false positive (two separated structures that
    # coincidentally sum to 5 bits before actually colliding).
    for step in range(1, 400):
        disc = step_grid(disc, lut)
        bc   = int(disc.sum())

        if bc != 5:
            continue

        rs, cs = np.where(disc > 0)
        row_span = int(max(rs)) - int(min(rs))
        col_span = int(max(cs)) - int(min(cs))

        # Compactness: a genuine fused composite fits in a ~6x6 bounding box.
        # Pre-fusion the L-tromino and 2-bit target area are ~30 rows apart.
        if row_span > 6 or col_span > 6:
            continue

        # Require 20 consecutive stable steps at 5 bits
        test = disc.copy()
        stable = True
        for _ in range(20):
            test = step_grid(test, lut)
            if int(test.sum()) != 5:
                stable = False
                break
        if stable:
            com_r  = float(np.mean(rs))
            com_c  = float(np.mean(cs))
            cr, cc = int(round(com_r)), int(round(com_c))
            offsets = sorted([(int(r) - cr, int(c) - cc)
                               for r, c in zip(rs, cs)])
            print(f"  Compact stable 5-bit found at step={step}")
            print(f"  CoM=({com_r:.2f},{com_c:.2f})  bbox=({row_span}x{col_span})")
            print(f"  cells={[(int(r),int(c)) for r,c in zip(rs,cs)]}")
            print(f"  Offsets from rounded CoM: {offsets}")
            return offsets, step

    # Fallback: any compact 5-bit (no stability requirement)
    print("  WARN: No compact stable 5-bit in 400 steps; relaxing to first compact occurrence")
    disc = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in [(32, 64), (33, 64), (33, 65)]:
        disc[r, c] = 1
    disc[64, 64] = 1
    for step in range(1, 500):
        disc = step_grid(disc, lut)
        bc = int(disc.sum())
        if bc != 5:
            continue
        rs, cs = np.where(disc > 0)
        if int(max(rs)) - int(min(rs)) <= 6 and int(max(cs)) - int(min(cs)) <= 6:
            com_r  = float(np.mean(rs))
            com_c  = float(np.mean(cs))
            cr, cc = int(round(com_r)), int(round(com_c))
            offsets = sorted([(int(r) - cr, int(c) - cc)
                               for r, c in zip(rs, cs)])
            print(f"  Fallback compact 5-bit at step={step}")
            return offsets, step

    return None, None


def rotate_180(offsets):
    return [(-dr, -dc) for dr, dc in offsets]


def place_pattern(grid, offsets, anchor_r, anchor_c):
    placed = []
    for dr, dc in offsets:
        r = (anchor_r + dr) % GRID_SIZE
        c = (anchor_c + dc) % GRID_SIZE
        grid[r, c] = 1
        placed.append((r, c))
    return placed


def verify_direction(lut, offsets, anchor_r, anchor_c, n_steps=40):
    """
    Run n_steps on an isolated test grid; return (row_displacement, final_bits).
    Negative displacement → West; positive → East.
    """
    test = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    place_pattern(test, offsets, anchor_r, anchor_c)
    com_r0 = center_of_mass(test)[0]
    for _ in range(n_steps):
        test = step_grid(test, lut)
    bc_f   = int(test.sum())
    com_rf = center_of_mass(test)[0]
    disp   = com_rf - com_r0
    # Unwrap torus
    if disp >  GRID_SIZE / 2:
        disp -= GRID_SIZE
    if disp < -GRID_SIZE / 2:
        disp += GRID_SIZE
    return disp, bc_f


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=== iter_185.2 — Asymmetric Collision: 3-bit (East) vs 5-bit (West) ===")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}   Steps: {SIM_STEPS}")

    lut = load_rule()
    print(f"LUT: {len(lut)} entries, non-zero={int(lut.sum())}")

    # ── Phase 1: discover 5-bit composite ─────────────────────────────────────
    offsets_e, disc_step = discover_5bit_glider(lut)
    if offsets_e is None:
        print("ERROR: Could not extract 5-bit glider pattern")
        return 1

    offsets_w = rotate_180(offsets_e)
    print(f"\n  East offsets: {offsets_e}")
    print(f"  West offsets (180° rot): {offsets_w}")

    # ── Phase 1b: verify West motion of rotated 5-bit ─────────────────────────
    print("\n[Phase 1b] Verifying West motion of rotated 5-bit pattern (40 steps)")
    disp_w, bc_verify = verify_direction(lut, offsets_w, anchor_r=96, anchor_c=64)
    print(f"  Row displacement in 40 steps: {disp_w:.2f}  final_bits={bc_verify}")
    if disp_w < -5:
        direction_tag = "West-confirmed"
        print("  Result: moves West as expected")
    elif disp_w > 5:
        direction_tag = "East-unexpected"
        print("  Result: pattern moves East (180° symmetry not satisfied for 5-bit)")
    else:
        direction_tag = f"unclear(disp={disp_w:.1f})"
        print(f"  Result: unclear motion (disp={disp_w:.2f})")

    # Also verify the 3-bit still moves East
    print("\n[Phase 1c] Verifying 3-bit L-tromino moves East (40 steps)")
    tromino_offsets = [(0, 0), (1, 0), (1, 1)]
    disp_3, bc_3 = verify_direction(lut, tromino_offsets, anchor_r=32, anchor_c=64)
    print(f"  Row displacement in 40 steps: {disp_3:.2f}  final_bits={bc_3}")

    # ── Phase 2: set up collision grid ────────────────────────────────────────
    print("\n[Phase 2] Setting up collision grid")
    # 3-bit L-tromino (East) at (32, 64)
    # 5-bit composite (West) at (96, 64)
    # → 64 rows apart, meet near row 64 at ~step 32
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)

    cells_3bit = place_pattern(grid, tromino_offsets, 32, 64)
    cells_5bit = place_pattern(grid, offsets_w, 96, 64)

    print(f"  3-bit cells (East):  {sorted(cells_3bit)}")
    print(f"  5-bit cells (West):  {sorted(cells_5bit)}")

    initial_bits = int(grid.sum())
    print(f"  Initial bit count: {initial_bits}  (expected 8 = 3+5)")
    if initial_bits != 8:
        print(f"  WARNING: overlap or mis-placement! got {initial_bits} bits")

    # ── Phase 3: run 500-step simulation ──────────────────────────────────────
    print(f"\n[Phase 3] Simulating {SIM_STEPS} steps…")
    frames      = [(0, grid.copy())]
    bit_counts  = [initial_bits]
    max_bits    = initial_bits
    min_bits    = initial_bits
    collision_step = None

    print(f"{'step':>6}  {'bits':>6}  {'com_r':>8}  {'com_c':>8}")
    print("-" * 42)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        if bc > max_bits:
            max_bits = bc
        if bc < min_bits:
            min_bits = bc

        if collision_step is None and bc != initial_bits:
            collision_step = step

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            com_r, com_c = center_of_mass(grid)
            print(f"{step:>6}  {bc:>6}  {com_r:>8.2f}  {com_c:>8.2f}")

    final_bits = bit_counts[-1]
    final_com  = center_of_mass(grid)

    print()
    print("=== Results ===")
    print(f"Initial bits:   {initial_bits}")
    print(f"Final bits:     {final_bits}")
    print(f"Max bits:       {max_bits}")
    print(f"Min bits:       {min_bits}")
    print(f"Collision step: {collision_step}")
    print(f"Final CoM:      ({final_com[0]:.2f},{final_com[1]:.2f})")
    print(f"Direction tag:  {direction_tag}")

    # Classify outcome
    all_conserved = all(bc == initial_bits for bc in bit_counts)
    if final_bits == 0:
        outcome = "annihilation"
    elif all_conserved:
        outcome = "elastic"
    elif final_bits == initial_bits:
        outcome = "bit_conserved_after_disturbance"
    elif max_bits > 3 * initial_bits:
        outcome = ("explosive_growth_then_stabilize"
                   if final_bits < max_bits // 2 else "explosive_growth")
    elif final_bits < initial_bits and final_bits > 0:
        outcome = f"partial_annihilation_debris_{final_bits}bits"
    elif final_bits > initial_bits:
        outcome = f"net_creation_{final_bits}bits"
    else:
        outcome = "inelastic_complex"
    print(f"Outcome:        {outcome}")

    # ── Phase 4: save animation ───────────────────────────────────────────────
    print(f"\n[Phase 4] Saving {len(frames)}-frame animation -> {GIF_PATH.name}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        "Asymmetric Collision: 3-bit (East) vs 5-bit (West)\ng10_rule_001",
        color="white", fontsize=10,
    )
    ax.set_xlabel("col", color="white", fontsize=8)
    ax.set_ylabel("row", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for sp in ax.spines.values():
        sp.set_edgecolor("white")

    step0, g0 = frames[0]
    img  = ax.imshow(g0, origin="upper", interpolation="nearest",
                     cmap="hot", vmin=0, vmax=1)
    info = ax.text(0.02, 0.97, f"step=0  bits={initial_bits}",
                   transform=ax.transAxes, color="white", fontsize=9, va="top")

    def update(fi):
        step, g = frames[fi]
        img.set_data(g)
        info.set_text(f"step={step}  bits={bit_counts[step]}")
        return img, info

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                   interval=FRAME_MS, blit=True)
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Saved: {GIF_PATH}")

    print("\n=== Final Summary ===")
    print(f"  initial_bits:   {initial_bits}")
    print(f"  final_bits:     {final_bits}")
    print(f"  max_bits:       {max_bits}")
    print(f"  min_bits:       {min_bits}")
    print(f"  collision_step: {collision_step}")
    print(f"  outcome:        {outcome}")
    print(f"  direction_tag:  {direction_tag}")
    print(f"  5bit_disc_step: {disc_step}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

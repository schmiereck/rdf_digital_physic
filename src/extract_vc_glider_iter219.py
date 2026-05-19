#!/usr/bin/env python3
"""
extract_vc_glider_iter219.py

Robustly extracts the v<c glider structure from iter_218's champion rule g4_rule_083.

Strategy:
1. Load chromosome from champion_rule.json
2. Run dense (toroidal) simulation with L-tromino seed for 200 steps,
   saving snapshots at steps 50 and 100.
3. Find connected components at step 100.
4. Test each component (and the full cell set) in sparse (infinite-grid)
   isolation for 40 steps to measure displacement.
5. Components with displacement > 1 cell are part of the glider.
6. Normalize the glider's coordinates so top-left = [0, 0].
7. Save to archive/iter_219/results/vc_glider_g4_rule_083_structure.json.
"""

import json
import math
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_218" / "results" / "champion_rule.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_219" / "results"
OUTPUT_PATH  = RESULTS_DIR / "vc_glider_g4_rule_083_structure.json"

GRID_SIZE = 128

# Hexagonal neighborhood encoding (matches step_grid / run_simulation.py):
# bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
# In (row, col) offsets:
HEX_DIRS = [
    ( 1,  0),   # E  → bit5
    ( 1, -1),   # SE → bit4
    ( 0, -1),   # SW → bit3
    (-1,  0),   # W  → bit2
    (-1,  1),   # NW → bit1
    ( 0,  1),   # NE → bit0
]


# ── Dense simulation on toroidal grid ─────────────────────────────────────────

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


# ── Sparse simulation on infinite grid ────────────────────────────────────────

def nbr_value(cells_set: frozenset, q: int, r: int) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_sparse(cells: frozenset, chrom: list) -> frozenset:
    candidates: set = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))
    new_cells: set = set()
    for q, r in candidates:
        nbr = nbr_value(cells, q, r)
        if chrom[nbr]:
            new_cells.add((q, r))
    return frozenset(new_cells)


def cells_com(cells) -> tuple:
    n = len(cells)
    return (sum(q for q, r in cells) / n, sum(r for q, r in cells) / n)


def displacement(cells_start, cells_end) -> float:
    q0, r0 = cells_com(cells_start)
    q1, r1 = cells_com(cells_end)
    return math.sqrt((q1 - q0) ** 2 + (r1 - r0) ** 2)


# ── Connected components on toroidal grid ──────────────────────────────────────

def find_components(grid: np.ndarray, grid_size: int = GRID_SIZE) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    components = []
    for start in live:
        if start in visited:
            continue
        comp: set = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            comp.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % grid_size, (r + dr) % grid_size)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(frozenset(comp))
    return components


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load rule
    with open(CHAMP_PATH) as f:
        data = json.load(f)

    chrom = data["chromosome"]       # 128-element list of 0/1
    lut   = np.array(chrom, dtype=np.uint8)
    print(f"Loaded champion rule: chromosome length={len(chrom)}, "
          f"non-zero entries={sum(chrom)}")

    # Seed: L-tromino, centered so we have plenty of room to row ~116 before wrapping
    # seed_particle from JSON = [[0,0],[0,1],[1,1]]
    # Seed at row=32, col=32 → at step 100 the glider is at ~row 74, step 200 at ~row 116
    seed_origin_r, seed_origin_c = 32, 32
    seed_offsets = data.get("seed_particle", [[0, 0], [0, 1], [1, 1]])

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for cell in seed_offsets:
        r = (seed_origin_r + cell[0]) % GRID_SIZE
        c = (seed_origin_c + cell[1]) % GRID_SIZE
        grid[r, c] = 1

    init_cells = sorted(map(tuple, np.argwhere(grid == 1)))
    print(f"Initial cells (seed): {init_cells}")
    print(f"Initial bit count: {int(grid.sum())}")

    # Run simulation, recording snapshots
    grid50  = None
    grid100 = None

    for step in range(1, 201):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        if step == 50:
            grid50 = grid.copy()
            print(f"Step  50: {bc} live cells, "
                  f"positions={sorted(map(tuple, np.argwhere(grid == 1)))}")
        elif step == 100:
            grid100 = grid.copy()
            print(f"Step 100: {bc} live cells, "
                  f"positions={sorted(map(tuple, np.argwhere(grid == 1)))}")
        elif step == 200:
            print(f"Step 200: {bc} live cells, "
                  f"positions={sorted(map(tuple, np.argwhere(grid == 1)))}")

    # ── Identify glider at step 100 ───────────────────────────────────────────

    cells100 = frozenset(map(tuple, np.argwhere(grid100 == 1)))
    cells50  = frozenset(map(tuple, np.argwhere(grid50 == 1)))

    print(f"\nCells at step 50:  {sorted(cells50)}")
    print(f"Cells at step 100: {sorted(cells100)}")
    print(f"COM step 50:  {cells_com(cells50)}")
    print(f"COM step 100: {cells_com(cells100)}")

    # Gross displacement from step 50 → step 100 (no wrap needed; both ~row 50-90)
    gross_disp_50_100 = displacement(cells50, cells100)
    print(f"COM displacement step 50→100: {gross_disp_50_100:.4f} cells")

    # Connected components at step 100
    comps100 = find_components(grid100)
    print(f"\nConnected components at step 100: {len(comps100)}")
    for i, comp in enumerate(comps100):
        print(f"  Component {i}: size={len(comp)}, cells={sorted(comp)}, "
              f"com={cells_com(comp)}")

    # ── Test A: Run all live cells together in isolation for 40 steps ─────────
    ISOLATION_STEPS = 40
    test_group = cells100
    init_com_group = cells_com(test_group)
    for _ in range(ISOLATION_STEPS):
        test_group = step_sparse(test_group, chrom)
        if not test_group:
            break
    group_disp = 0.0
    if test_group:
        group_disp = displacement(cells100, test_group)
    print(f"\nGroup isolation test ({ISOLATION_STEPS} steps): "
          f"displacement={group_disp:.4f}, final size={len(test_group)}")

    # ── Test B: Test each connected component in isolation ────────────────────
    comp_results = []
    for i, comp in enumerate(comps100):
        test = comp
        init_com_c = cells_com(test)
        for _ in range(ISOLATION_STEPS):
            test = step_sparse(test, chrom)
            if not test:
                break
        if test:
            disp = displacement(comp, test)
        else:
            disp = 0.0
        print(f"  Component {i} isolated {ISOLATION_STEPS} steps: "
              f"displacement={disp:.4f}, final_size={len(test) if test else 0}")
        comp_results.append((i, comp, disp, test))

    # ── Classify components as glider vs debris ───────────────────────────────
    MOVEMENT_THRESHOLD = 1.0  # cells

    glider_cells: set = set()
    debris_cells: set = set()

    if group_disp > MOVEMENT_THRESHOLD:
        # All cells move together → all are the glider
        print("\nAll cells move together in isolation → all are the glider.")
        glider_cells = set(cells100)
    else:
        # Classify individually
        for i, comp, disp, test in comp_results:
            if disp > MOVEMENT_THRESHOLD:
                glider_cells.update(comp)
            else:
                debris_cells.update(comp)
        print(f"\nClassification: {len(glider_cells)} glider cells, "
              f"{len(debris_cells)} debris cells")

    if not glider_cells:
        print("ERROR: No glider cells identified!")
        return 1

    print(f"\nGlider cells at step 100: {sorted(glider_cells)}")

    # ── Normalize coordinates: min_row=0, min_col=0 ───────────────────────────
    cells_sorted = sorted(glider_cells)
    min_r = min(r for r, c in cells_sorted)
    min_c = min(c for r, c in cells_sorted)

    normalized = sorted([[r - min_r, c - min_c] for r, c in cells_sorted])

    print(f"\nNormalized glider coordinates (top-left at [0, 0]):")
    for coord in normalized:
        print(f"  {coord}")

    bit_count = len(normalized)
    print(f"\nGlider bit count: {bit_count}")

    # ── Save to JSON ──────────────────────────────────────────────────────────
    with open(OUTPUT_PATH, "w") as f:
        json.dump(normalized, f, indent=2)
    print(f"Saved: {OUTPUT_PATH}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

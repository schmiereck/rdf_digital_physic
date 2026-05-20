#!/usr/bin/env python3
"""
run_evolution_exp_222.py  —  72-orbit C2-symmetric evolutionary search

A 50-generation evolutionary search that operates directly on the 72-orbit
C2-symmetric chromosome representation.  The 128-state local-neighborhood
LUT factors into 72 orbits under C2 (180°) hex rotation:
  - 16 states fixed by C2 (orbit size 1)
  - 56 orbits of size 2
  16 + 56 = 72 orbits.

A length-72 binary chromosome (one bit per orbit, the output center bit)
is sufficient to specify any C2-symmetric rule.

Fitness: per-step unwrapped CoM tracking + DisplacementConsistencyFitness
        (num_windows=5, max_bit_threshold=12, max_velocity_threshold=0.9,
         min_velocity=0.02).

GA:
  population_size = 100   generations = 50   elite = 10
  tournament size = 3     crossover prob = 0.5    mutation prob = 0.02/bit

Warm start: archive/iter_215/results/final_population.json (100 rules).

Outputs (archive/iter_222/results/):
  champion_rule_perfect.json
  evolution_summary_perfect.csv
  champion_vc_glider_perfect.gif
  trajectory_analysis.txt
"""

from __future__ import annotations

import csv
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid          # noqa: E402
from new_fitness import DisplacementConsistencyFitness     # noqa: E402

# ── Configuration ────────────────────────────────────────────────────────────

OUTPUT_DIR      = PROJECT_ROOT / "archive" / "iter_222" / "results"
WARM_START_PATH = PROJECT_ROOT / "archive" / "iter_215" / "results" / "final_population.json"

POPULATION_SIZE = int(os.environ.get("POPULATION_SIZE", 100))
GENERATIONS     = int(os.environ.get("GENERATIONS", 50))
ELITE_SIZE      = int(os.environ.get("ELITE_SIZE", 10))
TOURNAMENT_SIZE = 3
CROSSOVER_PROB  = 0.5
MUTATION_PROB   = 0.02
GRID_SIZE       = 128
STEPS           = 500
LUT_SIZE        = 128
RNG_SEED        = 222

# DisplacementConsistencyFitness parameters
NUM_WINDOWS     = 5
MAX_BIT_THRESHOLD = 12
MAX_VEL_THRESHOLD = 0.9
MIN_VEL         = 0.02

SEED_CELLS      = [(63, 63), (64, 63), (64, 64)]

NUM_WORKERS     = int(os.environ.get("NUM_WORKERS", max(1, (os.cpu_count() or 4) - 1)))

# ── C2 orbit machinery ───────────────────────────────────────────────────────
#
# Neighborhood-state bit layout (MSB first):
#   bit 6 = center
#   bit 5 = E      bit 2 = W
#   bit 4 = SE     bit 1 = NW
#   bit 3 = SW     bit 0 = NE
#
# C2 = 180° rotation swaps E↔W, SE↔NW, SW↔NE; center is fixed.

def _c2_rotate(state: int) -> int:
    c  = (state >> 6) & 1
    e  = (state >> 5) & 1
    se = (state >> 4) & 1
    sw = (state >> 3) & 1
    w  = (state >> 2) & 1
    nw = (state >> 1) & 1
    ne = (state >> 0) & 1
    # 180° rotation: E↔W, SE↔NW, SW↔NE
    return (c << 6) | (w << 5) | (nw << 4) | (ne << 3) | (e << 2) | (se << 1) | sw


def _build_orbit_tables():
    """Return (orbit_idx_of_state, orbit_reps) for the 72-orbit C2 structure.

    orbit_idx_of_state[s] -> integer orbit index in [0, 72)
    orbit_reps[i]         -> canonical (min-state) representative of orbit i
    """
    canonical_of = [None] * LUT_SIZE
    for s in range(LUT_SIZE):
        c2 = _c2_rotate(s)
        canonical_of[s] = min(s, c2)
    unique_reps = sorted(set(canonical_of))
    rep_to_idx = {rep: i for i, rep in enumerate(unique_reps)}
    orbit_idx_of_state = [rep_to_idx[canonical_of[s]] for s in range(LUT_SIZE)]
    return orbit_idx_of_state, unique_reps


ORBIT_IDX_OF_STATE, ORBIT_REPS = _build_orbit_tables()
NUM_ORBITS = len(ORBIT_REPS)
assert NUM_ORBITS == 72, f"Expected 72 orbits, got {NUM_ORBITS}"


# ── Chromosome <-> rule_dict conversions ─────────────────────────────────────

def chromosome_72_to_rule_dict(chrom_72) -> dict:
    """Convert a length-72 binary chromosome to a sparse rule_dict.

    The rule_dict only stores entries where the output center bit differs
    from the input center bit (identity default).  This matches the
    representation used by ``rule_dict_to_lut`` in evolution.py.
    """
    out: dict = {}
    chrom = list(chrom_72)
    for s in range(LUT_SIZE):
        orbit_idx = ORBIT_IDX_OF_STATE[s]
        output_c  = int(chrom[orbit_idx])
        default_c = (s >> 6) & 1
        if output_c != default_c:
            out[s] = (output_c << 6) | (s & 0b0111111)
    return out


def rule_dict_to_chromosome_72(rule_dict: dict) -> np.ndarray:
    chrom = np.zeros(NUM_ORBITS, dtype=np.uint8)
    members_per_orbit = [[] for _ in range(NUM_ORBITS)]
    for s in range(LUT_SIZE):
        members_per_orbit[ORBIT_IDX_OF_STATE[s]].append(s)
    for i, members in enumerate(members_per_orbit):
        default_c = (ORBIT_REPS[i] >> 6) & 1
        any_in_rule = any(s in rule_dict for s in members)
        if any_in_rule:
            chrom[i] = 1 - default_c
        else:
            chrom[i] = default_c
    return chrom


def chromosome_72_to_lut(chrom_72) -> np.ndarray:
    """Build the boolean-center LUT used by step_grid directly from chrom_72.

    Equivalent to rule_dict_to_lut(chromosome_72_to_rule_dict(chrom_72))
    but skips the intermediate dict.
    """
    chrom = np.asarray(chrom_72, dtype=np.uint8)
    lut = np.zeros(LUT_SIZE, dtype=np.uint8)
    for s in range(LUT_SIZE):
        lut[s] = chrom[ORBIT_IDX_OF_STATE[s]]
    return lut


# ── Simulation with perfect unwrapped CoM ────────────────────────────────────

def _unwrap_com(prev_com, raw_com, grid_size=GRID_SIZE):
    pr, pc = prev_com
    cr, cc = raw_com
    half = grid_size / 2.0
    dr = cr - pr
    dc = cc - pc
    if dr > half:
        cr -= grid_size
    elif dr < -half:
        cr += grid_size
    if dc > half:
        cc -= grid_size
    elif dc < -half:
        cc += grid_size
    return (cr, cc)


def _com_and_bits(grid):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def _simulate_history_from_lut(lut: np.ndarray, steps: int = STEPS) -> list:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    raw_c0, b0 = _com_and_bits(grid)
    prev_raw = (raw_c0[0], raw_c0[1])
    # accumulator for fully unwrapped CoM
    unwrapped = prev_raw
    hist = [{"step": 0, "com": unwrapped, "bit_count": b0}]

    for t in range(1, steps + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = _com_and_bits(grid)
        if bc == 0:
            # particle gone — stop tracking position, but record bit_count=0
            hist.append({"step": t, "com": unwrapped, "bit_count": 0})
            # keep prev_raw unchanged
            continue
        # unwrap raw_c relative to prev_raw
        unwrapped_step = _unwrap_com(prev_raw, raw_c)
        # accumulate by adding the unwrapped delta to the unwrapped accumulator
        dx = unwrapped_step[0] - prev_raw[0]
        dy = unwrapped_step[1] - prev_raw[1]
        unwrapped = (unwrapped[0] + dx, unwrapped[1] + dy)
        prev_raw = raw_c
        hist.append({"step": t, "com": unwrapped, "bit_count": bc})

    return hist


# ── Module-level worker for ProcessPoolExecutor ──────────────────────────────

_FITNESS_FN = DisplacementConsistencyFitness(
    num_windows=NUM_WINDOWS,
    max_bit_threshold=MAX_BIT_THRESHOLD,
    max_velocity_threshold=MAX_VEL_THRESHOLD,
    min_velocity=MIN_VEL,
)


def evaluate_chromosome(chrom_72_list):
    """Worker function (must be at module level so it is picklable).

    Takes a chromosome as a Python list of ints (picklable), simulates
    500 steps with perfect unwrapped CoM, and returns the fitness float.
    """
    chrom = np.array(chrom_72_list, dtype=np.uint8)
    lut = chromosome_72_to_lut(chrom)
    hist = _simulate_history_from_lut(lut, STEPS)
    score = _FITNESS_FN(hist)
    return float(score)


# ── Warm-start loading ───────────────────────────────────────────────────────

def load_warm_start_chromosomes_72(path: Path):
    """Load rules from final_population.json and project to 72-orbit chroms.

    Returns a list of np.ndarray (length 72, dtype uint8).
    """
    if not path.is_file():
        return []
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        # try common keys
        for k in ("population", "entries", "items", "population_list"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break
    if not isinstance(data, list):
        return []

    chroms = []
    for entry in data:
        if isinstance(entry, dict):
            rd = entry.get("rule_dict")
        else:
            continue
        if rd is None:
            continue
        rd_int = {int(k): int(v) for k, v in rd.items()}
        chrom = rule_dict_to_chromosome_72(rd_int)
        chroms.append(chrom)
    return chroms


def _mutate_bits(chrom: np.ndarray, rng: random.Random, prob: float) -> np.ndarray:
    out = chrom.copy()
    n = len(out)
    for i in range(n):
        if rng.random() < prob:
            out[i] ^= 1
    return out


def _random_chromosome(rng: random.Random) -> np.ndarray:
    return np.array([rng.randint(0, 1) for _ in range(NUM_ORBITS)], dtype=np.uint8)


# ── GA operations ────────────────────────────────────────────────────────────

def tournament_select(population, scores, rng, k=TOURNAMENT_SIZE):
    candidates = rng.sample(range(len(population)), k)
    best = candidates[0]
    best_score = scores[best]
    for c in candidates[1:]:
        if scores[c] > best_score:
            best = c
            best_score = scores[c]
    return population[best]


def uniform_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random) -> np.ndarray:
    mask = np.array([rng.randint(0, 1) for _ in range(NUM_ORBITS)], dtype=np.uint8)
    child = np.where(mask == 1, p1, p2).astype(np.uint8)
    return child


def select_top_k(population, scores, k):
    order = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Parallel evaluation ─────────────────────────────────────────────────────

def evaluate_population_parallel(population, executor):
    args = [chrom.tolist() for chrom in population]
    scores = list(executor.map(evaluate_chromosome, args, chunksize=4))
    return scores


# ── CSV / printing ───────────────────────────────────────────────────────────

def write_evolution_summary_csv(gen_log, path: Path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["generation", "best_fitness", "mean_fitness"])
        writer.writeheader()
        for entry in gen_log:
            writer.writerow({
                "generation":   entry["generation"],
                "best_fitness": f'{entry["best_fitness"]:.6f}',
                "mean_fitness": f'{entry["mean_fitness"]:.6f}',
            })


def print_evolution_summary(gen_log):
    print(f"{'Gen':>5s}  {'Best Fitness':>15s}  {'Mean Fitness':>15s}")
    print(f"{'-'*5}  {'-'*15}  {'-'*15}")
    for entry in gen_log:
        print(
            f'{entry["generation"]:>5d}  '
            f'{entry["best_fitness"]:>15.6f}  '
            f'{entry["mean_fitness"]:>15.6f}'
        )


# ── GIF renderer ────────────────────────────────────────────────────────────

def render_champion_gif(rule_dict: dict, gif_path: Path, steps: int = 500, stride: int = 5):
    print(f"Rendering GIF -> {gif_path}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED_CELLS:
        grid[r, c] = 1

    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % stride == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title("Champion v<c Glider (iter 222, 72-orbit C2)")
    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    txt = ax.text(
        0.02, 0.97, f"step={frames[0][0]}", transform=ax.transAxes,
        color="white", fontsize=10, va="top",
    )

    def update(i):
        step, g = frames[i]
        img.set_data(g)
        txt.set_text(f"step={step}")
        return img, txt

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=80, blit=True,
    )
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(gif_path), writer="pillow", fps=12)
    plt.close(fig)
    print(f"GIF saved ({gif_path.stat().st_size/1024:.1f} KB)")


# ── 500-step champion characterisation ──────────────────────────────────────

def characterise_champion(rule_dict: dict, txt_path: Path, fitness: float):
    """Run a 500-step characterisation of the champion, write analysis txt."""
    lut = rule_dict_to_lut(rule_dict)
    history = _simulate_history_from_lut(lut, 500)

    # Pull out trajectories
    bits = [h["bit_count"] for h in history]
    coms = [h["com"] for h in history]
    steps = [h["step"] for h in history]

    extinction_step = None
    for i, b in enumerate(bits):
        if b == 0:
            extinction_step = steps[i]
            break

    initial_bits = bits[0]
    final_bits = bits[-1]
    max_bits = max(bits)
    min_bits_alive = min(b for b in bits if b > 0) if any(b > 0 for b in bits) else 0

    initial_com = coms[0]
    final_com = coms[-1]
    dx = final_com[0] - initial_com[0]
    dy = final_com[1] - initial_com[1]
    total_disp = math.sqrt(dx * dx + dy * dy)
    speed = total_disp / 500.0 if extinction_step is None else (
        math.sqrt(
            (coms[extinction_step - 1][0] - initial_com[0]) ** 2 +
            (coms[extinction_step - 1][1] - initial_com[1]) ** 2
        ) / max(1, extinction_step - 1)
    )

    # Estimate period by looking for bit-count cycles after step 50
    period = None
    if extinction_step is None:
        tail = bits[50:]
        # try periods up to 50
        for p in range(1, 51):
            ok = True
            for i in range(p, min(len(tail), 200)):
                if tail[i] != tail[i - p]:
                    ok = False
                    break
            if ok:
                period = p
                break

    grown_without_bound = max_bits > MAX_BIT_THRESHOLD * 2 or final_bits > MAX_BIT_THRESHOLD * 2

    if extinction_step is not None:
        verdict = f"EXTINCT at step {extinction_step} — NOT a stable glider"
    elif grown_without_bound:
        verdict = f"GROWING WITHOUT BOUND (max_bits={max_bits}) — NOT a stable glider"
    elif speed <= 0 or speed >= 1.0:
        verdict = f"INVALID SPEED ({speed:.4f}) — NOT a v<c glider"
    elif speed < MIN_VEL:
        verdict = f"BELOW min_velocity ({speed:.6f} < {MIN_VEL}) — too slow"
    else:
        verdict = f"STABLE v<c GLIDER  (speed = {speed:.6f} cells/step)"

    # Build trajectory snapshots at 10 equally spaced steps
    snapshot_indices = list(range(0, 501, 50))
    lines = []
    lines.append("=" * 78)
    lines.append("CHAMPION TRAJECTORY ANALYSIS (iter 222, 72-orbit C2 search)")
    lines.append("=" * 78)
    lines.append("")
    lines.append(f"Fitness                : {fitness:.6f}")
    lines.append(f"Steps simulated        : 500")
    lines.append(f"Seed                   : L-tromino at (63,63),(64,63),(64,64)")
    lines.append(f"Grid                   : {GRID_SIZE}x{GRID_SIZE} toroidal")
    lines.append("")
    lines.append("Bit-count statistics")
    lines.append("-" * 78)
    lines.append(f"  initial bits         : {initial_bits}")
    lines.append(f"  final bits           : {final_bits}")
    lines.append(f"  max bits (any step)  : {max_bits}")
    lines.append(f"  min bits while alive : {min_bits_alive}")
    lines.append(f"  extinction step      : {extinction_step}")
    if period is not None:
        lines.append(f"  detected period      : {period} steps (bit_count sequence repeats)")
    else:
        lines.append(f"  detected period      : not detected within 50 steps")
    lines.append("")
    lines.append("Centre-of-mass trajectory (unwrapped, perfectly continuous)")
    lines.append("-" * 78)
    lines.append(f"  initial CoM          : ({initial_com[0]:+.4f}, {initial_com[1]:+.4f})")
    lines.append(f"  final CoM            : ({final_com[0]:+.4f}, {final_com[1]:+.4f})")
    lines.append(f"  total Δ              : (Δr={dx:+.4f}, Δc={dy:+.4f})")
    lines.append(f"  total displacement   : {total_disp:.4f} cells")
    lines.append(f"  mean speed |v|       : {speed:.6f} cells/step  ({speed*100:.3f}% of c=1)")
    lines.append("")
    lines.append("v < c verdict")
    lines.append("-" * 78)
    lines.append(f"  {verdict}")
    lines.append("")
    lines.append("Snapshots every 50 steps")
    lines.append("-" * 78)
    lines.append(f"  {'step':>5s} {'bit_count':>10s} {'CoM row':>12s} {'CoM col':>12s}")
    for s_idx in snapshot_indices:
        if s_idx <= len(history) - 1:
            h = history[s_idx]
            lines.append(
                f"  {h['step']:>5d} {h['bit_count']:>10d} "
                f"{h['com'][0]:>12.4f} {h['com'][1]:>12.4f}"
            )

    # Also report per-window velocities
    lines.append("")
    lines.append("Per-window mean velocity magnitudes (5 windows of 100 steps)")
    lines.append("-" * 78)
    total_steps = float(history[-1]["step"] - history[0]["step"])
    steps_per_window = total_steps / NUM_WINDOWS
    for w in range(NUM_WINDOWS):
        ws = int(w * steps_per_window)
        we = int((w + 1) * steps_per_window) if w < NUM_WINDOWS - 1 else int(total_steps)
        h_a = history[ws]
        h_b = history[we]
        wdx = h_b["com"][0] - h_a["com"][0]
        wdy = h_b["com"][1] - h_a["com"][1]
        wsteps = h_b["step"] - h_a["step"]
        mag = math.sqrt(wdx * wdx + wdy * wdy) / wsteps if wsteps > 0 else 0.0
        lines.append(
            f"  window {w}: steps {h_a['step']:3d}..{h_b['step']:3d}  "
            f"Δr={wdx:+.4f}  Δc={wdy:+.4f}  |v|={mag:.6f}"
        )
    lines.append("")
    lines.append("=" * 78)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote trajectory analysis -> {txt_path}")
    return {
        "extinction_step": extinction_step,
        "speed": speed,
        "total_disp": total_disp,
        "max_bits": max_bits,
        "period": period,
        "verdict": verdict,
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print("=== run_evolution_exp_222 (72-orbit C2 GA) ===")
    print(f"  pop={POPULATION_SIZE}  gens={GENERATIONS}  elite={ELITE_SIZE}  "
          f"tourn={TOURNAMENT_SIZE}  xover={CROSSOVER_PROB}  mut={MUTATION_PROB}/bit")
    print(f"  steps={STEPS}  fitness=DisplacementConsistencyFitness("
          f"num_windows={NUM_WINDOWS}, max_bit={MAX_BIT_THRESHOLD}, "
          f"max_vel={MAX_VEL_THRESHOLD}, min_vel={MIN_VEL})")
    print(f"  num_orbits={NUM_ORBITS}  workers={NUM_WORKERS}")
    print(f"  warm_start={WARM_START_PATH}")
    print()

    # Load warm-start chromosomes
    warm = load_warm_start_chromosomes_72(WARM_START_PATH)
    print(f"  Loaded {len(warm)} warm-start chromosomes from final_population.json")

    population = [c.copy() for c in warm[:POPULATION_SIZE]]
    if len(population) < POPULATION_SIZE:
        needed = POPULATION_SIZE - len(population)
        print(f"  Padding {needed} chromosomes by mutating warm starts...")
        seeds = warm if warm else [_random_chromosome(rng)]
        while len(population) < POPULATION_SIZE:
            parent = seeds[rng.randrange(len(seeds))]
            child = _mutate_bits(parent, rng, prob=0.05)  # heavier mutation for variety
            population.append(child)
    print(f"  Initial population: {len(population)} chromosomes (len={NUM_ORBITS})")
    print()

    t0 = time.time()

    champion_chrom = None
    champion_fitness = -1.0
    gen_log = []

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Generation 0 evaluation
        scores = evaluate_population_parallel(population, executor)
        best_idx = int(np.argmax(scores))
        if scores[best_idx] > champion_fitness:
            champion_fitness = float(scores[best_idx])
            champion_chrom = population[best_idx].copy()
        gen_log.append({
            "generation": 0,
            "best_fitness": float(np.max(scores)),
            "mean_fitness": float(np.mean(scores)),
        })
        print(f"  Gen  0: best={gen_log[-1]['best_fitness']:.6f}  "
              f"mean={gen_log[-1]['mean_fitness']:.6f}  "
              f"champion={champion_fitness:.6f}")

        # Evolution loop
        for gen in range(1, GENERATIONS + 1):
            elites = select_top_k(population, scores, ELITE_SIZE)
            next_pop = [e.copy() for e in elites]
            while len(next_pop) < POPULATION_SIZE:
                # Tournament selection
                p1 = tournament_select(population, scores, rng)
                # Crossover with prob CROSSOVER_PROB
                if rng.random() < CROSSOVER_PROB:
                    p2 = tournament_select(population, scores, rng)
                    child = uniform_crossover(p1, p2, rng)
                else:
                    child = p1.copy()
                # Mutation
                child = _mutate_bits(child, rng, MUTATION_PROB)
                next_pop.append(child)
            population = next_pop

            scores = evaluate_population_parallel(population, executor)
            best_idx = int(np.argmax(scores))
            if scores[best_idx] > champion_fitness:
                champion_fitness = float(scores[best_idx])
                champion_chrom = population[best_idx].copy()
                print(f"    ** new champion @ gen {gen}: {champion_fitness:.6f} **")

            gen_log.append({
                "generation": gen,
                "best_fitness": float(np.max(scores)),
                "mean_fitness": float(np.mean(scores)),
            })
            print(f"  Gen {gen:2d}: best={gen_log[-1]['best_fitness']:.6f}  "
                  f"mean={gen_log[-1]['mean_fitness']:.6f}  "
                  f"champion={champion_fitness:.6f}")

    elapsed = time.time() - t0
    print(f"\n=== Search complete in {elapsed:.1f}s ===")
    print(f"  Champion fitness: {champion_fitness:.6f}")

    # Save champion rule
    champ_rd = chromosome_72_to_rule_dict(champion_chrom)
    payload = {
        "fitness": champion_fitness,
        "fitness_function": "DisplacementConsistencyFitness",
        "fitness_params": {
            "num_windows": NUM_WINDOWS,
            "max_bit_threshold": MAX_BIT_THRESHOLD,
            "max_velocity_threshold": MAX_VEL_THRESHOLD,
            "min_velocity": MIN_VEL,
        },
        "ga_params": {
            "population_size": POPULATION_SIZE,
            "generations": GENERATIONS,
            "elite_size": ELITE_SIZE,
            "tournament_size": TOURNAMENT_SIZE,
            "crossover_prob": CROSSOVER_PROB,
            "mutation_prob": MUTATION_PROB,
            "representation": "72-orbit C2-symmetric chromosome",
        },
        "horizon": STEPS,
        "grid_size": GRID_SIZE,
        "seed_particle": "L_TROMINO_3bit",
        "seed_cells": [list(c) for c in SEED_CELLS],
        "elapsed_sec": round(elapsed, 2),
        "rule_dict": {str(k): int(v) for k, v in champ_rd.items()},
        "chromosome_72": [int(b) for b in champion_chrom],
        "warm_start": str(WARM_START_PATH),
        "unwrapped_com": "perfect_continuous_step_accumulated",
    }
    champion_path = OUTPUT_DIR / "champion_rule_perfect.json"
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved champion rule  -> {champion_path}")

    # Save CSV
    summary_path = OUTPUT_DIR / "evolution_summary_perfect.csv"
    write_evolution_summary_csv(gen_log, summary_path)
    print(f"Saved evolution summary -> {summary_path}")

    # Render GIF
    gif_path = OUTPUT_DIR / "champion_vc_glider_perfect.gif"
    render_champion_gif(champ_rd, gif_path)

    # Characterise champion (500 steps)
    txt_path = OUTPUT_DIR / "trajectory_analysis.txt"
    char = characterise_champion(champ_rd, txt_path, champion_fitness)

    # Print final tables
    print("\n=== Evolution Summary ===")
    print_evolution_summary(gen_log)

    print("\n=== Champion characterisation ===")
    print(f"  extinction_step : {char['extinction_step']}")
    print(f"  speed           : {char['speed']:.6f} cells/step")
    print(f"  total_disp      : {char['total_disp']:.4f}")
    print(f"  max_bits        : {char['max_bits']}")
    print(f"  period          : {char['period']}")
    print(f"  verdict         : {char['verdict']}")


if __name__ == "__main__":
    main()

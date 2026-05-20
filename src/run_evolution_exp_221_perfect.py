#!/usr/bin/env python3
"""
run_evolution_exp_221_perfect.py  -  30-generation evolutionary search for a stable glider
                              (perfect cell-unwrapped CoM tracking)

Uses DisplacementConsistencyFitness (new_fitness.py) with the 3-bit L-tromino
seed to search for hexagonal CA rules that produce consistent, directional motion.

KEY FEATURE: The `simulate_with_history` helper performs *continuous unwrapped
CoM tracking* during the simulation loop. At every step the raw (toroidal) CoM
is unwrapped relative to the previous raw CoM so that toroidal boundary crossings
do not create artificial jumps in the position record. The unwrapped CoM is then
stored in the history passed to ``DisplacementConsistencyFitness``, which in turn
does an additional defensive unwrap — but because the history already contains
fully unwrapped CoM values, the net result is correct even for rules that
produce gliders crossing grid boundaries many times over 500 steps.

Parameters:
  population_size : 100
  generations     : 30
  elite_size      : 10
  mutation_rate   : 0.01
  horizon         : 500 steps

Warm-start: loads initial population from archive/iter_215/results/final_population.json

Outputs:
  archive/iter_221/results/champion_rule_perfect.json
  archive/iter_221/results/evolution_summary_perfect.csv
  archive/iter_221/results/champion_vc_glider_perfect.gif
"""

from __future__ import annotations

import csv
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import generate_random_c2_rule, rule_dict_to_lut, step_grid  # noqa: E402
from new_fitness import DisplacementConsistencyFitness                     # noqa: E402

OUTPUT_DIR      = PROJECT_ROOT / "archive" / "iter_221" / "results"
POPULATION_SIZE = int(os.environ.get("POPULATION_SIZE", 100))
GENERATIONS     = int(os.environ.get("GENERATIONS", 30))
ELITE_SIZE      = int(os.environ.get("ELITE_SIZE", 10))
MUTATION_RATE   = 0.01
GRID_SIZE       = 128
STEPS           = 500
LUT_SIZE        = 128
RNG_SEED        = 221
WARM_START_PATH = PROJECT_ROOT / "archive" / "iter_215" / "results" / "final_population.json"

# Ensure elite size makes sense relative to population size
if ELITE_SIZE > POPULATION_SIZE:
    ELITE_SIZE = POPULATION_SIZE


# ── Chromosome helpers ────────────────────────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            v = (actual_center << 6) | (s & 0b0111111)
            out[s] = v
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Perfect unwrapped CoM simulation ─────────────────────────────────────────

def com_and_bits(grid: np.ndarray, grid_size: int = GRID_SIZE) -> tuple[tuple[float, float], int]:
    """Return the *raw toroidal* centre of mass and bit count for a grid.

    Parameters
    ----------
    grid : np.ndarray of uint8, shape (H, W)
    grid_size : int

    Returns
    -------
    com : (row, col) tuple  --  raw CoM in [0, grid_size)
    bits : int
    """
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())


def _unwrap_com(prev_com: tuple[float, float], raw_com: tuple[float, float],
                grid_size: int = GRID_SIZE) -> tuple[float, float]:
    """Unwrap one raw CoM step relative to the previous raw CoM.

    The grid wraps at *grid_size*.  If the difference between
    consecutive raw CoM positions exceeds half the grid size in either
    direction, we subtract/add *grid_size* to remove the toroidal
    discontinuity.

    Returns the unwrapped (absolute, non-wrapping) position.
    """
    pr, pc = prev_com
    cr, cc = raw_com
    half   = grid_size / 2.0

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


def simulate_with_history(rule_dict: dict) -> list:
    """Run a CA simulation and return a history with **perfectly unwrapped** CoM.

    The CoM is unwrapped at *every* step so that toroidal boundary crossings
    do not create artificial jumps.  This allows the downstream
    ``DisplacementConsistencyFitness`` to correctly measure sustained
    directional motion and correctly filter out v=1c gliders (which travel
    at speed-of-light and exceed the 0.9 velocity threshold).

    Returns
    -------
    history : list[dict]
        Each dict has ``'step'``, ``'com'`` (unwrapped), ``'bit_count'``.
    """
    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    # --- Continuous unwrapped CoM tracking ---
    raw_c0, b0 = com_and_bits(grid)
    prev_raw   = (raw_c0[0], raw_c0[1])          # step 0: unwrapped == raw
    hist = [{"step": 0, "com": prev_raw, "bit_count": b0}]

    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        raw_c, bc = com_and_bits(grid)

        # Unwrap the raw CoM relative to the PREVIOUS raw CoM
        unwrapped = _unwrap_com(prev_raw, raw_c)
        prev_raw  = raw_c                       # update for next iteration

        hist.append({"step": t, "com": unwrapped, "bit_count": bc})

    return hist


# ── Fitness evaluator ─────────────────────────────────────────────────────────

_fitness_fn = DisplacementConsistencyFitness(
    num_windows=5,
    max_bit_threshold=12,
    max_velocity_threshold=0.9,
    min_velocity=0.05,
)


def evaluate_rule(rule_dict: dict) -> float:
    hist  = simulate_with_history(rule_dict)
    score = _fitness_fn(hist)
    return float(score)


# ── Warm-start population loading ─────────────────────────────────────────────

def load_warm_start_population(warm_start_dir: Path, population_size: int,
                               rng: random.Random) -> list[np.ndarray]:
    """
    Load initial population from a saved final_population.json file.

    Returns a list of numpy arrays (chromosomes), padded or truncated
    to *population_size*.  Falls back to None if file not found.
    """
    candidates = [
        warm_start_dir / "final_population.json",
        warm_start_dir / "warm_start_population.json",
    ]

    for json_path in candidates:
        if not json_path.is_file():
            print(f"  Warm-start file not found: {json_path}")
            continue

        print(f"  Found warm-start candidate: {json_path}")
        with open(json_path) as f:
            data = json.load(f)

        # Handle two known structures:
        # 1) Top-level list
        # 2) Top-level dict with 'population' key
        entries = None
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = data.get("population", None)
            if entries is None:
                for k in ("entries", "items", "population_list"):
                    if k in data:
                        entries = data[k]
                        break

        if entries is None or not isinstance(entries, list):
            print(f"    Skipping: top-level is not a list with 'population' key")
            continue

        # Extract chromosomes
        chromosomes = []
        for entry in entries:
            if isinstance(entry, dict):
                chrom = entry.get("chromosome", None)
            elif isinstance(entry, list):
                chrom = entry
            else:
                continue

            if chrom is not None and len(chrom) == LUT_SIZE:
                chromosomes.append(np.array(chrom, dtype=np.uint8))

        if len(chromosomes) > 0:
            print(f"    Loaded {len(chromosomes)} chromosomes from {json_path.name}")
            if len(chromosomes) < population_size:
                needed = population_size - len(chromosomes)
                print(f"    Padding with {needed} random chromosomes")
                while len(chromosomes) < population_size:
                    rule = generate_random_c2_rule(rng)
                    chromosomes.append(rule_dict_to_chromosome(rule))
            else:
                rng.shuffle(chromosomes)
                chromosomes = chromosomes[:population_size]

            return chromosomes

    return None


# ── Population helpers ────────────────────────────────────────────────────────

def generate_population(size: int, rng: random.Random) -> list[np.ndarray]:
    pop: list[np.ndarray] = []
    while len(pop) < size:
        rule = generate_random_c2_rule(rng)
        pop.append(rule_dict_to_chromosome(rule))
    return pop[:size]


def evaluate_population(population: list[np.ndarray]) -> list[float]:
    scores: list[float] = []
    for i, chrom in enumerate(population):
        rd    = chromosome_to_rule_dict(chrom)
        score = evaluate_rule(rd)
        scores.append(score)
        if (i + 1) % 25 == 0:
            print(f"    ... evaluated {i + 1}/{len(population)}")
    return scores


def select_top_k(population, scores, k):
    order = sorted(range(len(population)), key=lambda i: scores[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


def swap_mutate(chrom: np.ndarray, num_swaps: int, rng: random.Random) -> np.ndarray:
    out = chrom.copy()
    n   = len(out)
    for _ in range(num_swaps):
        i, j     = rng.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
    return out


# ── CSV writer ────────────────────────────────────────────────────────────────

def write_evolution_summary_csv(gen_log: list[dict], path: Path) -> None:
    """Write the evolution summary to a CSV file using the standard csv module."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["generation", "best_fitness", "mean_fitness"])
        writer.writeheader()
        for entry in gen_log:
            writer.writerow({
                "generation":   entry["generation"],
                "best_fitness": f'{entry["best_fitness"]:.6f}',
                "mean_fitness": f'{entry["mean_fitness"]:.6f}',
            })


def print_evolution_summary(gen_log: list[dict]) -> None:
    """Print a plain-text table of the evolution summary."""
    print(f"{'Gen':>5s}  {'Best Fitness':>15s}  {'Mean Fitness':>15s}")
    print(f"{'-'*5}  {'-'*15}  {'-'*15}")
    for entry in gen_log:
        print(
            f'{entry["generation"]:>5d}  '
            f'{entry["best_fitness"]:>15.6f}  '
            f'{entry["mean_fitness"]:>15.6f}'
        )


# ── GIF renderer ──────────────────────────────────────────────────────────────

def render_champion_gif(rule_dict: dict, gif_path: Path, steps: int = 500, stride: int = 5) -> None:
    """Render a GIF of the champion glider moving in the grid."""
    print(f"Rendering GIF -> {gif_path}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    lut  = rule_dict_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    grid[63, 63] = 1
    grid[64, 63] = 1
    grid[64, 64] = 1

    frames = [(0, grid.copy())]
    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        if step % stride == 0 or step == steps:
            frames.append((step, grid.copy()))

    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title("Champion v<c Glider (iter 221 perfect unwrapped)")
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


# ── Main evolution loop ──────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng       = random.Random(RNG_SEED)
    num_swaps = max(1, round(MUTATION_RATE * LUT_SIZE))

    print("=== run_evolution_exp_221_perfect ===")
    print(f"  population={POPULATION_SIZE}  generations={GENERATIONS}  "
          f"elite={ELITE_SIZE}  swaps/child={num_swaps}  horizon={STEPS}")
    print(f"  Warm start from: {WARM_START_PATH}")
    print(f"  Fitness: DisplacementConsistencyFitness("
          f"num_windows=5, max_bit_threshold=12, "
          f"max_velocity_threshold=0.9, min_velocity=0.05)")
    print()

    t0         = time.time()

    # --- Load warm-start population ---
    if WARM_START_PATH.exists():
        print(f"  Loading {POPULATION_SIZE} chromosomes from warm start...")
        population = load_warm_start_population(
            WARM_START_PATH.parent, POPULATION_SIZE, rng
        )
        if population is not None:
            print(f"  Loaded {len(population)} chromosomes from warm start.")
        else:
            print("  Warm start file has no valid chromosomes; generating random population...")
            population = generate_population(POPULATION_SIZE, rng)
    else:
        print("  Warm start file not found, generating random population...")
        population = generate_population(POPULATION_SIZE, rng)

    champion_chrom:   np.ndarray | None = None
    champion_fitness: float             = -1.0
    gen_log: list[dict] = []

    # - Evaluate generation 0 - - - - - - - - - - - - - - - - - - - - - - - - - -

    scores = evaluate_population(population)
    best_idx = int(np.argmax(scores))
    if scores[best_idx] > champion_fitness:
        champion_fitness = float(scores[best_idx])
        champion_chrom   = population[best_idx].copy()

    gen_log.append({
        "generation":   0,
        "best_fitness": float(np.max(scores)),
        "mean_fitness": float(np.mean(scores)),
    })
    print(f"  Gen  0: best={gen_log[-1]['best_fitness']:.6f}  "
          f"mean={gen_log[-1]['mean_fitness']:.6f}")

    # - Generational loop - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    for gen in range(1, GENERATIONS + 1):
        elites   = select_top_k(population, scores, ELITE_SIZE)
        next_pop = [e.copy() for e in elites]
        while len(next_pop) < POPULATION_SIZE:
            parent = rng.choice(elites)
            child  = swap_mutate(parent, num_swaps, rng)
            next_pop.append(child)
        population = next_pop

        scores   = evaluate_population(population)
        best_idx = int(np.argmax(scores))

        if scores[best_idx] > champion_fitness:
            champion_fitness = float(scores[best_idx])
            champion_chrom   = population[best_idx].copy()
            print(f"    ** new champion @ gen {gen}: {champion_fitness:.6f} **")

        gen_log.append({
            "generation":   gen,
            "best_fitness": float(np.max(scores)),
            "mean_fitness": float(np.mean(scores)),
        })
        print(f"  Gen {gen:2d}: best={gen_log[-1]['best_fitness']:.6f}  "
              f"mean={gen_log[-1]['mean_fitness']:.6f}  "
              f"champion={champion_fitness:.6f}")

    elapsed = time.time() - t0
    print(f"\n=== Search complete in {elapsed:.1f}s ===")
    print(f"  Champion fitness: {champion_fitness:.6f}")

    # - Save champion rule - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    champ_rd = chromosome_to_rule_dict(champion_chrom)
    payload  = {
        "fitness":          champion_fitness,
        "fitness_function": "DisplacementConsistencyFitness",
        "fitness_params":   {
            "num_windows": 5,
            "max_bit_threshold": 12,
            "max_velocity_threshold": 0.9,
            "min_velocity": 0.05,
        },
        "generations":      GENERATIONS,
        "population_size":  POPULATION_SIZE,
        "elite_size":       ELITE_SIZE,
        "mutation_rate":    MUTATION_RATE,
        "horizon":          STEPS,
        "grid_size":        GRID_SIZE,
        "seed_particle":    "L_TROMINO_3bit",
        "seed_cells":       [[63, 63], [64, 63], [64, 64]],
        "elapsed_sec":      round(elapsed, 2),
        "rule_dict":        {str(k): int(v) for k, v in champ_rd.items()},
        "chromosome":       [int(b) for b in champion_chrom],
        "warm_start":       str(WARM_START_PATH),
        "unwrapped_com":    "perfect_continuous",   # perfect per-step unwrapping
    }

    champion_path = OUTPUT_DIR / "champion_rule_perfect.json"
    with open(champion_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved champion rule  -> {champion_path}")

    # - Save evolution summary CSV - - - - - - - - - - - - - - - - - - - - - - -

    summary_path = OUTPUT_DIR / "evolution_summary_perfect.csv"
    write_evolution_summary_csv(gen_log, summary_path)
    print(f"Saved evolution summary -> {summary_path}")

    # - Render and save GIF of champion - - - - - - - - - - - - - - - - - - - - -

    gif_path = OUTPUT_DIR / "champion_vc_glider_perfect.gif"
    render_champion_gif(champ_rd, gif_path)

    # - Print summary table - - - - - - - - - - - - - - - - - - - - - - - - - - -

    print("\n=== Evolution Summary ===")
    print_evolution_summary(gen_log)

    # Check for plateau: compare last 5 gens vs first 5 gens
    gen0_mean  = gen_log[0]["mean_fitness"]
    gen_n_mean = gen_log[-1]["mean_fitness"]
    improved   = gen_n_mean > gen0_mean * 1.5
    print(f"\n  mean_fitness gen0:  {gen0_mean:.6f}")
    print(f"  mean_fitness genN:  {gen_n_mean:.6f}")
    print(f"  Fitness improved significantly: {improved}")


if __name__ == "__main__":
    main()

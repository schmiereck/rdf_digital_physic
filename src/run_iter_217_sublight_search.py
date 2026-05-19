#!/usr/bin/env python3
"""
run_iter_217_sublight_search.py

Evolutionary search for v<c gliders (iter_217).

Warm-starts from the iter_215 population (mix of iter_213/176/153 champions
and their per-bit mutants), then runs up to 10 generations of GA using the
SubLightFitness function that enforces:
  - velocity gate: avg_velocity < 0.9 cells/step
  - period gate:   period > 1

Halts early if any individual achieves fitness > 0 (confirmed v<c glider).

Outputs:
  archive/iter_217/results/champion.json            (if glider found)
  archive/iter_217/results/champion_vc_glider.gif   (if glider found)
  archive/iter_217/results/best_failure.json        (if no glider found)
"""
from __future__ import annotations

import concurrent.futures
import json
import random
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fitness_functions import SubLightFitness

PROJECT_ROOT    = Path(__file__).parent.parent
WARM_START_PATH = PROJECT_ROOT / "archive" / "iter_215" / "results" / "warm_start_population.json"
OUTPUT_DIR      = PROJECT_ROOT / "archive" / "iter_217" / "results"

LUT_SIZE        = 128
LTROMINO        = [(0, 0), (0, 1), (1, 1)]
RNG_SEED        = 217_001
ELITE_FRACTION  = 0.10
CROSSOVER_RATE  = 0.80
MUTATION_RATE   = 0.01
MAX_GENERATIONS = 10
POPULATION_SIZE = 100
GRID_SIZE       = 128
ANIM_STEPS      = 200
ZOOM            = 32
MAX_WORKERS     = 8


# ── Chromosome helpers ─────────────────────────────────────────────────────────

def chromosome_to_rule_dict(chrom: np.ndarray) -> dict:
    out: dict = {}
    for s in range(LUT_SIZE):
        default_center = (s >> 6) & 1
        actual_center  = int(chrom[s])
        if actual_center != default_center:
            out[s] = (actual_center << 6) | (s & 0b0111111)
    return out


def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


# ── Worker (module-level so ProcessPoolExecutor can pickle it) ─────────────────

_FITNESS: SubLightFitness | None = None


def _eval_worker(chrom_list: list) -> dict:
    global _FITNESS
    if _FITNESS is None:
        _FITNESS = SubLightFitness()
    chrom     = np.asarray(chrom_list, dtype=np.uint8)
    rule_dict = chromosome_to_rule_dict(chrom)
    fitness, metrics = _FITNESS(rule_dict)
    return {"fitness": float(fitness), "metrics": metrics}


# ── Genetic operators ──────────────────────────────────────────────────────────

def two_point_crossover(p1: np.ndarray, p2: np.ndarray, rng: random.Random):
    n = len(p1)
    a, b = sorted(rng.sample(range(n + 1), 2))
    c1, c2 = p1.copy(), p2.copy()
    c1[a:b] = p2[a:b]
    c2[a:b] = p1[a:b]
    return c1, c2


def per_bit_mutation(chrom: np.ndarray, rate: float, rng: random.Random) -> np.ndarray:
    for i in range(len(chrom)):
        if rng.random() < rate:
            chrom[i] ^= 1
    return chrom


def select_top_k(population: list, fitnesses: list, k: int) -> list:
    order = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
    return [population[i].copy() for i in order[:k]]


# ── Animation helpers ──────────────────────────────────────────────────────────

def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def _torus_com(grid: np.ndarray, grid_size: int) -> tuple[float, float]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0)
    twopi    = 2.0 * np.pi
    a_r      = twopi * rows.astype(float) / grid_size
    com_r    = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * grid_size / twopi
    a_c      = twopi * cols.astype(float) / grid_size
    com_c    = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * grid_size / twopi
    return (float(com_r), float(com_c))


def _render_frame(cells, com, grid_size: int, zoom: int = ZOOM) -> np.ndarray:
    r_c   = int(round(com[0])) % grid_size
    c_c   = int(round(com[1])) % grid_size
    size  = 2 * zoom
    frame = np.zeros((size, size), dtype=np.float32)
    half  = grid_size // 2
    for r, c in cells:
        dr = (int(r) - r_c + half) % grid_size - half
        dc = (int(c) - c_c + half) % grid_size - half
        if -zoom <= dr < zoom and -zoom <= dc < zoom:
            frame[dr + zoom, dc + zoom] = 1.0
    return frame


def save_glider_gif(rule_dict: dict, output_path: Path, n_steps: int = ANIM_STEPS) -> None:
    lut    = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    lut = ((lut >> 6) & 1).astype(np.uint8)

    grid   = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    centre = GRID_SIZE // 2
    for dr, dc in LTROMINO:
        grid[(centre + dr) % GRID_SIZE, (centre + dc) % GRID_SIZE] = 1

    frames_cells: list = []
    frames_com:   list = []

    rs, cs = np.where(grid > 0)
    frames_cells.append(list(zip(rs.tolist(), cs.tolist())))
    frames_com.append(_torus_com(grid, GRID_SIZE))

    for _ in range(n_steps):
        grid = _step_grid(grid, lut)
        rs, cs = np.where(grid > 0)
        frames_cells.append(list(zip(rs.tolist(), cs.tolist())))
        frames_com.append(_torus_com(grid, GRID_SIZE))

    fig_g, ax_g = plt.subplots(figsize=(4, 4), dpi=80)
    fig_g.subplots_adjust(0, 0, 1, 1)
    ax_g.set_axis_off()
    frame0 = _render_frame(frames_cells[0], frames_com[0], GRID_SIZE)
    im  = ax_g.imshow(frame0, cmap="binary", vmin=0, vmax=1,
                      interpolation="nearest", origin="upper")
    txt = ax_g.text(0.02, 0.97, "Step 0", transform=ax_g.transAxes,
                    color="red", fontsize=7, va="top",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6))

    def _update(i: int):
        fr  = _render_frame(frames_cells[i], frames_com[i], GRID_SIZE)
        im.set_data(fr)
        com = frames_com[i]
        txt.set_text(f"Step {i}  ({com[0]:.1f}, {com[1]:.1f})")
        return [im, txt]

    anim = FuncAnimation(fig_g, _update, frames=n_steps + 1, interval=50, blit=True)
    anim.save(str(output_path), writer=PillowWriter(fps=20))
    plt.close(fig_g)
    print(f"Saved GIF: {output_path}")


# ── Population loading ─────────────────────────────────────────────────────────

def load_warm_start() -> list[np.ndarray]:
    with open(WARM_START_PATH) as f:
        data = json.load(f)
    population = [
        np.asarray(ind["chromosome"], dtype=np.uint8)
        for ind in data["population"]
    ]
    rng = random.Random(RNG_SEED)
    while len(population) < POPULATION_SIZE:
        population.append(population[rng.randrange(len(population))].copy())
    return population[:POPULATION_SIZE]


# ── Parallel evaluation ────────────────────────────────────────────────────────

def evaluate_population(population: list) -> tuple[list, list]:
    tasks = [c.tolist() for c in population]
    out   = [None] * len(tasks)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(_eval_worker, t): i for i, t in enumerate(tasks)}
        for fut in concurrent.futures.as_completed(futs):
            i      = futs[fut]
            out[i] = fut.result()
    fitnesses = [r["fitness"] for r in out]
    metrics   = [r["metrics"] for r in out]
    return fitnesses, metrics


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0  = time.time()
    rng = random.Random(RNG_SEED)

    print("=== iter_217 SubLight Evolutionary Search ===")
    print(f"  Fitness function : SubLightFitness (vel_gate<0.9, period_gate>1)")
    print(f"  Max generations  : {MAX_GENERATIONS}")
    print(f"  Population size  : {POPULATION_SIZE}")
    print(f"  Warm-start file  : {WARM_START_PATH}")

    population  = load_warm_start()
    elite_count = max(2, int(POPULATION_SIZE * ELITE_FRACTION))
    print(f"  Loaded {len(population)} individuals  elite_count={elite_count}")

    best_fitness    = -1.0
    best_chrom: np.ndarray | None = None
    best_metrics: dict | None     = None
    best_generation = -1
    found_glider    = False
    stats: list[dict] = []

    for gen in range(MAX_GENERATIONS + 1):
        print(f"\n--- Generation {gen} ---", flush=True)
        fitnesses, metrics_l = evaluate_population(population)

        gen_max     = float(np.max(fitnesses))
        gen_mean    = float(np.mean(fitnesses))
        n_nonzero   = sum(1 for f in fitnesses if f > 0.0)
        reason_cnts: dict[str, int] = {}
        for m in metrics_l:
            r = m.get("reason", "unknown")
            reason_cnts[r] = reason_cnts.get(r, 0) + 1

        print(f"  max={gen_max:.6f}  mean={gen_mean:.8f}  non_zero={n_nonzero}")
        print(f"  reasons: {reason_cnts}")

        stats.append({
            "generation":    gen,
            "max":           gen_max,
            "mean":          gen_mean,
            "non_zero":      n_nonzero,
            "reason_counts": reason_cnts,
        })

        best_idx = int(np.argmax(fitnesses))
        if fitnesses[best_idx] > best_fitness:
            best_fitness    = fitnesses[best_idx]
            best_chrom      = population[best_idx].copy()
            best_metrics    = metrics_l[best_idx]
            best_generation = gen

        if best_fitness > 0.0:
            found_glider = True
            print(f"\n*** v<c GLIDER FOUND at generation {gen}! "
                  f"fitness={best_fitness:.6f} ***")
            break

        if gen == MAX_GENERATIONS:
            break

        # Breed next generation
        elite   = select_top_k(population, fitnesses, elite_count)
        new_pop = [e.copy() for e in elite]
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.sample(elite, 2)
            if rng.random() < CROSSOVER_RATE:
                c1, c2 = two_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()
            c1 = per_bit_mutation(c1, MUTATION_RATE, rng)
            c2 = per_bit_mutation(c2, MUTATION_RATE, rng)
            new_pop.append(c1)
            if len(new_pop) < POPULATION_SIZE:
                new_pop.append(c2)
        population = new_pop

    elapsed = time.time() - t0
    print(f"\n=== Search complete in {elapsed:.1f}s ===")
    print(f"  Best fitness    : {best_fitness:.6f}")
    print(f"  Best generation : {best_generation}")
    print(f"  Found glider    : {found_glider}")

    assert best_chrom is not None
    best_rule = chromosome_to_rule_dict(np.asarray(best_chrom, dtype=np.uint8))
    artifacts: list[str] = []

    if found_glider:
        champion = {
            "fitness":     best_fitness,
            "generation":  best_generation,
            "metrics":     best_metrics,
            "rule_dict":   {str(k): int(v) for k, v in best_rule.items()},
            "chromosome":  list(map(int, best_chrom)),
            "fitness_fn":  "SubLightFitness",
            "elapsed_sec": round(elapsed, 2),
            "stats":       stats,
        }
        champ_path = OUTPUT_DIR / "champion.json"
        with open(champ_path, "w") as f:
            json.dump(champion, f, indent=2)
        print(f"Saved: {champ_path}")
        artifacts.append(f"archive/iter_217/results/champion.json")

        gif_path = OUTPUT_DIR / "champion_vc_glider.gif"
        save_glider_gif(best_rule, gif_path)
        artifacts.append(f"archive/iter_217/results/champion_vc_glider.gif")

        status = "ok"
        exp_view = (
            f"v<c glider found at generation {best_generation} with "
            f"fitness={best_fitness:.6f}. "
            f"Metrics: avg_velocity={best_metrics.get('avg_velocity', 'N/A')}, "
            f"period={best_metrics.get('period', 'N/A')}."
        )
    else:
        failure = {
            "note":         "No v<c glider found after 10 generations",
            "best_fitness": best_fitness,
            "generation":   best_generation,
            "metrics":      best_metrics,
            "rule_dict":    {str(k): int(v) for k, v in best_rule.items()},
            "chromosome":   list(map(int, best_chrom)),
            "fitness_fn":   "SubLightFitness",
            "elapsed_sec":  round(elapsed, 2),
            "stats":        stats,
        }
        fail_path = OUTPUT_DIR / "best_failure.json"
        with open(fail_path, "w") as f:
            json.dump(failure, f, indent=2)
        print(f"Saved: {fail_path}")
        artifacts.append(f"archive/iter_217/results/best_failure.json")

        status   = "experiment_failed"
        last_reasons = stats[-1]["reason_counts"] if stats else {}
        exp_view = (
            f"No v<c glider found after {len(stats)} generations. "
            f"All individuals scored fitness=0. "
            f"Final generation reason counts: {last_reasons}. "
            f"Best metrics: {best_metrics}."
        )

    last_stat = stats[-1] if stats else {}
    artifacts_yaml = "\n".join(f"  - {a}" for a in artifacts)

    print(f"""
```yaml
status: {status}
artifacts:
{artifacts_yaml}
metrics:
  best_fitness: {best_fitness:.6f}
  best_generation: {best_generation}
  total_generations_run: {len(stats)}
  elapsed_sec: {round(elapsed, 1)}
  found_glider: {str(found_glider).lower()}
  final_gen_max: {last_stat.get('max', 0.0):.6f}
  final_gen_non_zero: {last_stat.get('non_zero', 0)}
log_excerpt: |
  Best fitness: {best_fitness:.6f}  generation: {best_generation}
  Found glider: {found_glider}
  Total generations: {len(stats)}
  Elapsed: {round(elapsed, 1)}s
  Final gen reason counts: {last_stat.get('reason_counts', {})}
experimenter_view: |
  {exp_view}
notes: iter_217 sublight evolutionary search using SubLightFitness with vel<0.9 and period>1 gates
```""")
    return 0


if __name__ == "__main__":
    sys.exit(main())

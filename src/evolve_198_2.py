#!/usr/bin/env python3
"""
evolve_198_2.py

DEAP-based evolutionary search for hex-CA glider rules using
EXPERIMENT_CONFIG from experiments/exp_198_2_massive_glider.py.

Chromosome: 7 booleans encoding survive conditions S0-S6
(hexagonal CA has 6 neighbours so counts range 0-6).
Birth condition is fixed at B3.

Results are written to archive/iter_198.2/results/.
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from deap import base, creator, tools

sys.path.insert(0, str(Path(__file__).parent))

from experiments.exp_198_2_massive_glider import EXPERIMENT_CONFIG

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_198.2" / "results"

# Hex neighbourhood has 6 neighbours → survival counts 0–6 → 7 bits
N_SURVIVE_BITS = 7
BIRTH_COUNTS   = frozenset({3})   # B3 is fixed


# ── Rule encoding helpers ─────────────────────────────────────────────────────

def chromosome_to_rule_dict(survive_bits: list) -> dict:
    """Convert 7-bool survival chromosome to hex-CA rule_dict.

    State encoding: bit6=center, bits5-0=six neighbours.
    Only entries that differ from the identity default are stored.
    Output 64 → next state alive; output 0 → next state dead.
    """
    rule_dict: dict = {}
    for state in range(128):
        center = (state >> 6) & 1
        nb_count = bin(state & 0x3F).count("1")

        if center == 0:
            new_alive = nb_count in BIRTH_COUNTS
        else:
            idx = min(nb_count, N_SURVIVE_BITS - 1)
            new_alive = bool(survive_bits[idx])

        default_alive = bool(center)
        if new_alive != default_alive:
            rule_dict[state] = 64 if new_alive else 0

    return rule_dict


def survive_bits_to_rule_string(survive_bits) -> str:
    s_digits = "".join(str(i) for i, v in enumerate(survive_bits) if v)
    b_digits = "".join(str(k) for k in sorted(BIRTH_COUNTS))
    return f"B{b_digits}/S{s_digits}"


# ── DEAP evaluation ──────────────────────────────────────────────────────────

def evaluate(individual):
    rule_dict  = chromosome_to_rule_dict(individual)
    fitness_fn = EXPERIMENT_CONFIG["fitness_function"]
    seed       = EXPERIMENT_CONFIG["seed"]
    score      = fitness_fn(rule_dict, seed)
    return (float(score),)


# ── Main evolution routine ───────────────────────────────────────────────────

def run_evolution():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    cfg      = EXPERIMENT_CONFIG
    pop_size = cfg["population_size"]
    n_gen    = cfg["generations"]
    cx_prob  = cfg["cx_prob"]
    mut_rate = cfg["mutation_rate"]
    n_elites = cfg["num_elites"]

    random.seed(42)
    np.random.seed(42)

    # DEAP setup
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register(
        "individual",
        tools.initRepeat,
        creator.Individual,
        toolbox.attr_bool,
        n=N_SURVIVE_BITS,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate",   evaluate)
    toolbox.register("mate",       tools.cxUniform, indpb=0.5)
    toolbox.register("mutate",     tools.mutFlipBit, indpb=mut_rate)
    toolbox.register("select",     tools.selTournament, tournsize=3)

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(10)

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", np.min)
    stats.register("avg", np.mean)
    stats.register("max", np.max)

    log_rows:  list[dict] = []
    log_lines: list[str]  = []

    # ── Evaluate initial population ──────────────────────────────────────────
    for ind in pop:
        ind.fitness.values = toolbox.evaluate(ind)
    hof.update(pop)

    record = stats.compile(pop)
    line   = f"Gen 0: Max fitness = {record['max']:.6f}, Avg fitness = {record['avg']:.6f}"
    print(line)
    log_lines.append(line)
    log_rows.append({"gen": 0, "min": record["min"], "avg": record["avg"], "max": record["max"]})

    # ── Generation loop ──────────────────────────────────────────────────────
    for gen in range(1, n_gen + 1):
        elites   = list(map(toolbox.clone, tools.selBest(pop, n_elites)))
        offspring = toolbox.select(pop, len(pop) - n_elites)
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cx_prob:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutation
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Re-evaluate invalid
        for ind in offspring:
            if not ind.fitness.valid:
                ind.fitness.values = toolbox.evaluate(ind)

        pop[:] = elites + offspring
        hof.update(pop)

        record = stats.compile(pop)
        line   = (
            f"Gen {gen}: Max fitness = {record['max']:.6f}, "
            f"Avg fitness = {record['avg']:.6f}"
        )
        print(line)
        log_lines.append(line)
        log_rows.append({
            "gen": gen,
            "min": record["min"],
            "avg": record["avg"],
            "max": record["max"],
        })

    # ── Summarise ────────────────────────────────────────────────────────────
    champion         = hof[0]
    champion_fitness = champion.fitness.values[0]
    rule_string      = survive_bits_to_rule_string(champion)
    final_line       = (
        f"Champion rule {rule_string} found with fitness {champion_fitness:.6f}"
    )
    print(final_line)
    log_lines.append(final_line)

    # ── Save artifacts ───────────────────────────────────────────────────────

    # champion.txt
    (RESULTS_DIR / "champion.txt").write_text(rule_string, encoding="utf-8")

    # hall_of_fame.json
    hof_data = [
        {
            "rule":       survive_bits_to_rule_string(ind),
            "chromosome": list(map(int, ind)),
            "fitness":    ind.fitness.values[0],
        }
        for ind in hof
    ]
    (RESULTS_DIR / "hall_of_fame.json").write_text(
        json.dumps(hof_data, indent=2), encoding="utf-8"
    )

    # evolution_log.csv
    with open(RESULTS_DIR / "evolution_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["gen", "min", "avg", "max"])
        writer.writeheader()
        writer.writerows(log_rows)

    # fitness_plot.png
    gens = [r["gen"] for r in log_rows]
    maxs = [r["max"] for r in log_rows]
    avgs = [r["avg"] for r in log_rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(gens, maxs, label="Max fitness", marker="o")
    ax.plot(gens, avgs, label="Avg fitness", marker="x", linestyle="--")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("MassiveGliderFitness — Evolutionary Search (iter_198.2)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fitness_plot.png", dpi=100)
    plt.close(fig)

    print(f"\nResults saved to {RESULTS_DIR}")
    return champion_fitness, n_gen, log_lines, rule_string


if __name__ == "__main__":
    run_evolution()

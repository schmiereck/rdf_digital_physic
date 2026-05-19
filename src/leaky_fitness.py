#!/usr/bin/env python3
"""
leaky_fitness.py

A 'leaky' fitness function that rewards displacement while applying a
continuous penalty for bit-count changes — providing an evolutionary
gradient toward both motion and conservation simultaneously.

LeakySubLightFitness
--------------------
Inherits from ``CheckpointFitness`` but replaces the hard bit-conservation
fail with a soft penalty (``conservation_factor``).  The fitness function
still gates on the particle's mean velocity (rejecting any rule whose
average speed exceeds 0.9 cells/step), and uses net displacement as the
base score, just like ``SubLightFitness``.

Scoring formula
~~~~~~~~~~~~~~~

For each checkpoint:

    if bit_count == initial_bit_count:
        conservation_factor = 1.0
    else:
        conservation_factor = min(bit_count, initial_bit_count)
                              / max(bit_count, initial_bit_count)

    total_conservation_score = mean(conservation_factors across all checkpoints)

    base_fitness   = net_displacement  (Euclidean distance initial CoM -> final CoM)
    final_fitness  = base_fitness * total_conservation_score

The result is a smooth landscape: rules that move fast and conserve bits
score highest, while rules that lose or gain bits still earn fractional
fitness proportional to how closely they track the original mass.

Usage
~~~~~
    from src.leaky_fitness import LeakySubLightFitness

    fitness_fn = LeakySubLightFitness(
        checkpoints=[50, 100, 150],
        simulation_steps=200,
        bits_per_cell=1,
        velocity_threshold=0.9,
    )

    score = fitness_fn(rule, [(0, 0), (0, 1), (1, 1)])
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from simulator import Particle, Simulator


class LeakySubLightFitness:
    """Fitness that rewards displacement but *leaks* the bit-conservation gate.

    Parameters
    ----------
    checkpoints : list[int]
        Step indices at which to sample the particle's bit count.
    simulation_steps : int
        Total number of CA steps to run.
    bits_per_cell : int, optional
        Bits per cell for the simulation.  Defaults to the module default
        from ``engine.BITS_PER_CELL``.
    velocity_threshold : float, optional
        Hard upper bound on mean velocity (cells / step).  Particles whose
        average velocity meets or exceeds this threshold are rejected with
        fitness = 0.0.  Default 0.9 (the *sub-light* threshold).
    """

    name = "LeakySubLightFitness"

    def __init__(
        self,
        checkpoints: list[int],
        simulation_steps: int,
        bits_per_cell: int | None = None,
        velocity_threshold: float = 0.9,
    ) -> None:
        self.checkpoints: set[int] = set(checkpoints)
        self.simulation_steps: int = int(simulation_steps)
        self.bits_per_cell: int = int(
            bits_per_cell if bits_per_cell is not None else 1
        )
        self.velocity_threshold: float = float(velocity_threshold)

        if self.velocity_threshold <= 0.0 or self.velocity_threshold > 1.0:
            raise ValueError(
                f"velocity_threshold ({self.velocity_threshold}) must be "
                "in the range (0, 1]."
            )

    # ── public API ─────────────────────────────────────────────────────────

    def evaluate(self, rule, seed_bits: list[tuple[int, int]]) -> float:
        """Evaluate *rule* starting from *seed_bits* coordinates.

        Returns
        -------
        float
            ``base_fitness * total_conservation_score``, where
            ``base_fitness`` is the net displacement and
            ``total_conservation_score`` is the mean conservation factor
            across all checkpoints.

            Returns ``0.0`` when the particle's mean velocity exceeds the
            ``velocity_threshold``.
        """
        grid = np.zeros((128, 128), dtype=np.uint8)
        for r, c in seed_bits:
            grid[r, c] = 1

        particle = Particle(grid, bits_per_cell=self.bits_per_cell)
        simulator = Simulator(rule, bits_per_cell=self.bits_per_cell)

        initial_bits = particle.bit_count
        initial_com = particle.center_of_mass()

        # Track total displacement over the full simulation for velocity
        # calculation.
        total_displacement = 0.0
        prev_com = initial_com

        # Accumulate a conservation factor at each checkpoint.
        conservation_factors: list[float] = []

        for step in range(1, self.simulation_steps + 1):
            simulator.step(particle)

            current_com = particle.center_of_mass()
            dx = current_com[0] - prev_com[0]
            dy = current_com[1] - prev_com[1]
            total_displacement += math.sqrt(dx * dx + dy * dy)
            prev_com = current_com

            if step in self.checkpoints:
                if particle.bit_count == initial_bits:
                    conservation_factors.append(1.0)
                else:
                    conservation_factors.append(
                        min(particle.bit_count, initial_bits)
                        / max(particle.bit_count, initial_bits)
                    )

        # ── Velocity gate ────────────────────────────────────────────────
        avg_velocity = total_displacement / self.simulation_steps
        if avg_velocity >= self.velocity_threshold:
            return 0.0

        # ── Base fitness = net displacement (like SubLightFitness) ───────
        # Net displacement is the straight-line distance from initial COM
        # to the *final* COM (after all simulation steps).
        final_com = particle.center_of_mass()
        net_dx = final_com[0] - initial_com[0]
        net_dy = final_com[1] - initial_com[1]
        base_fitness = math.sqrt(net_dx * net_dx + net_dy * net_dy)

        # ── Conservation score (leaky) ───────────────────────────────────
        if conservation_factors:
            total_conservation_score: float = (
                sum(conservation_factors) / len(conservation_factors)
            )
        else:
            total_conservation_score = 1.0

        # ── Final score ──────────────────────────────────────────────────
        fitness = base_fitness * total_conservation_score
        return fitness

    def __call__(
        self, rule, seed_bits: list[tuple[int, int]]
    ) -> tuple[float, dict[str, Any]]:
        """Convenience callable returning ``(fitness, metrics_dict)``.

        Parameters
        ----------
        rule : dict or object with ``.rule_dict``
            The CA rule to evaluate.
        seed_bits : list of (row, col)
            Initial live-cell coordinates.

        Returns
        -------
        tuple[float, dict]
            ``(fitness, metrics)`` where *metrics* contains intermediate
            values (``base_fitness``, ``total_conservation_score``,
            ``avg_velocity``, conservation factors, etc.).
        """
        fitness = self.evaluate(rule, seed_bits)
        return fitness, self._build_metrics(rule, seed_bits)

    def _build_metrics(
        self, rule, seed_bits: list[tuple[int, int]]
    ) -> dict[str, Any]:
        """Build a metrics dict with intermediate evaluation values."""
        grid = np.zeros((128, 128), dtype=np.uint8)
        for r, c in seed_bits:
            grid[r, c] = 1

        particle = Particle(grid, bits_per_cell=self.bits_per_cell)
        simulator = Simulator(rule, bits_per_cell=self.bits_per_cell)

        initial_bits = particle.bit_count
        initial_com = particle.center_of_mass()

        total_displacement = 0.0
        prev_com = initial_com
        conservation_factors: list[float] = []

        for step in range(1, self.simulation_steps + 1):
            simulator.step(particle)
            current_com = particle.center_of_mass()
            dx = current_com[0] - prev_com[0]
            dy = current_com[1] - prev_com[1]
            total_displacement += math.sqrt(dx * dx + dy * dy)
            prev_com = current_com

            if step in self.checkpoints:
                if particle.bit_count == initial_bits:
                    conservation_factors.append(1.0)
                else:
                    conservation_factors.append(
                        min(particle.bit_count, initial_bits)
                        / max(particle.bit_count, initial_bits)
                    )

        avg_velocity = total_displacement / self.simulation_steps
        final_com = particle.center_of_mass()
        net_dx = final_com[0] - initial_com[0]
        net_dy = final_com[1] - initial_com[1]
        base_fitness = math.sqrt(net_dx * net_dx + net_dy * net_dy)
        total_conservation_score = (
            sum(conservation_factors) / len(conservation_factors)
            if conservation_factors
            else 1.0
        )
        fitness = base_fitness * total_conservation_score

        return {
            "fitness": fitness,
            "base_fitness": base_fitness,
            "total_conservation_score": total_conservation_score,
            "conservation_factors": conservation_factors,
            "avg_velocity": avg_velocity,
            "velocity_threshold": self.velocity_threshold,
            "velocity_rejected": avg_velocity >= self.velocity_threshold,
            "net_displacement": base_fitness,
            "initial_bits": initial_bits,
            "initial_com": initial_com,
            "final_com": final_com,
            "simulation_steps": self.simulation_steps,
        }

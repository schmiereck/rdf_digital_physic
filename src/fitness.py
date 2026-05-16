#!/usr/bin/env python3
"""
fitness.py

Fitness metrics for hexagonal CA rules.
  - calculate_velocity_stability: rewards sustained, constant-velocity motion.
  - CheckpointFitness: rewards stable bit-count throughout the simulation.
  - DynamicCollisionFitness: rewards rules that produce a true dynamic
    bit-and-object-conserving collision between two 3-bit gliders (approach
    followed by recession).
"""

import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

sys.path.insert(0, str(Path(__file__).parent))
from simulator import Particle, Simulator
from evolution import rule_dict_to_lut, step_grid


HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
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


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def calculate_velocity_stability(
    rule_dict: dict,
    initial_state: np.ndarray,
    steps_per_window: int = 400,
    num_windows: int = 3,
) -> tuple:
    """
    Calculates fitness based on the stability of velocity over multiple time windows.

    A stable glider should have a constant velocity, meaning a very low standard deviation.
    Decaying motion will have a high standard deviation because early windows have high
    velocity and later windows approach zero.

    Returns (fitness, velocities, std_dev) where fitness = 1 / (1 + std_dev).
    """
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(initial_state)

    # Record COM at the start of each window
    com_checkpoints = [_center_of_mass(grid)]

    for _ in range(num_windows):
        for __ in range(steps_per_window):
            grid = _step_grid(grid, lut)
        com_checkpoints.append(_center_of_mass(grid))

    velocities = []
    for i in range(num_windows):
        sq, sr = com_checkpoints[i]
        eq, er = com_checkpoints[i + 1]
        displacement = math.sqrt((eq - sq) ** 2 + (er - sr) ** 2)
        # Total displacement per window — proportional to speed since all windows
        # are the same length. This keeps std_dev on a scale where
        # 1/(1+std_dev) meaningfully separates stable from decaying motion.
        velocities.append(displacement)

    if len(velocities) < 2:
        return 0.0, velocities, 0.0

    std_dev = float(np.std(velocities))
    fitness  = 1.0 / (1.0 + std_dev)

    return fitness, velocities, std_dev


class CheckpointFitness:
    """Fitness metric that requires bit-count stability at regular checkpoints.

    A rule scores > 0 only if the particle's bit count equals the initial
    seed bit count at every checkpoint step.  The score itself is the
    Euclidean distance travelled by the centre of mass.  Any bit-count
    change at a checkpoint immediately returns 0.0 (early exit).
    """

    def __init__(self, checkpoints: list, simulation_steps: int):
        self.checkpoints = set(checkpoints)
        self.simulation_steps = simulation_steps

    def evaluate(self, rule, seed_bits: list) -> float:
        """Evaluate *rule* starting from *seed_bits* coordinates.

        Parameters
        ----------
        rule:
            A Rule instance (has .rule_dict).
        seed_bits:
            List of [row, col] pairs defining the initial live cells.

        Returns
        -------
        float
            Euclidean displacement of centre of mass, or 0.0 if any
            checkpoint reveals a bit-count mismatch.
        """
        grid = np.zeros((128, 128), dtype=np.uint8)
        for r, c in seed_bits:
            grid[r][c] = 1

        particle = Particle(grid)
        simulator = Simulator(rule)

        initial_bits = particle.bit_count
        initial_com = particle.center_of_mass()

        for step in range(1, self.simulation_steps + 1):
            simulator.step(particle)
            if step in self.checkpoints:
                if particle.bit_count != initial_bits:
                    return 0.0

        final_com = particle.center_of_mass()
        dx = final_com[0] - initial_com[0]
        dy = final_com[1] - initial_com[1]
        return math.sqrt(dx * dx + dy * dy)


# ── DynamicCollisionFitness ─────────────────────────────────────────────────

# 64x64 grid with two 3-bit gliders on a collision course.
_DYN_GRID_SIZE = 64
_DYN_OBJECT_A = [(30, 20), (31, 20), (30, 21)]
_DYN_OBJECT_B = [(33, 43), (34, 43), (33, 44)]
_DYN_INITIAL_BITS = len(_DYN_OBJECT_A) + len(_DYN_OBJECT_B)  # 6
_DYN_INITIAL_OBJECTS = 2

# 8-connectivity so that diagonally-adjacent cells of an L-tromino count as
# one connected component.
_DYN_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)


def _make_dynamic_collision_grid(grid_size: int = _DYN_GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _DYN_OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _DYN_OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


def _two_object_com_distance(grid: np.ndarray) -> float | None:
    """Return Euclidean distance between the two component COMs, or None if
    the grid does not contain exactly two connected components."""
    labels, n = label(grid, structure=_DYN_LABEL_STRUCTURE)
    if n != 2:
        return None
    coms = center_of_mass(grid, labels, [1, 2])
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


class DynamicCollisionFitness:
    """Fitness function that rewards a *dynamic* bit-conserving collision.

    Two 3-bit gliders are placed on a 64x64 toroidal grid:
      * Object 1 at (30,20), (31,20), (30,21)
      * Object 2 at (33,43), (34,43), (33,44)

    The simulation is run for ``horizon`` steps (default 100). Distances
    between the centres of mass of the two connected components are sampled
    at three time points: 0 (initial), horizon // 2 (midpoint) and horizon
    (final).

    Fitness is 1.0 iff ALL four conditions hold, else 0.0:
      1. Approach   : midpoint distance < initial distance
      2. Recession  : final distance    > midpoint distance
      3. Bit cons.  : final live cells  == 6
      4. Obj cons.  : final components  == 2
    """

    name = "DynamicCollisionFitness"

    def __init__(
        self,
        horizon: int = 100,
        grid_size: int = _DYN_GRID_SIZE,
        rule: dict | None = None,
    ) -> None:
        self.horizon = int(horizon)
        self.grid_size = int(grid_size)
        self.rule = rule

    # ── core evaluation ──────────────────────────────────────────────────

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("DynamicCollisionFitness: no rule supplied")

        lut = rule_dict_to_lut(rule_dict)
        grid = _make_dynamic_collision_grid(self.grid_size)

        # Initial distance — there are exactly two components by construction.
        initial_distance = _two_object_com_distance(grid)
        if initial_distance is None:
            # Should not happen given the fixed seed but guard anyway.
            return self._fail({
                "initial_distance": None,
                "midpoint_distance": None,
                "final_distance": None,
                "final_bit_count": int(grid.sum()),
                "final_object_count": 0,
            })

        midpoint_step = self.horizon // 2
        midpoint_distance: float | None = None
        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == midpoint_step:
                midpoint_distance = _two_object_com_distance(grid)

        final_bit_count = int(grid.sum())
        _, final_object_count = label(grid, structure=_DYN_LABEL_STRUCTURE)
        final_object_count = int(final_object_count)
        final_distance = _two_object_com_distance(grid)

        metrics = {
            "initial_distance":   float(initial_distance),
            "midpoint_distance":  (
                float(midpoint_distance) if midpoint_distance is not None else None
            ),
            "final_distance":     (
                float(final_distance) if final_distance is not None else None
            ),
            "final_bit_count":    final_bit_count,
            "final_object_count": final_object_count,
        }

        if midpoint_distance is None or final_distance is None:
            return self._fail(metrics)

        approach   = midpoint_distance < initial_distance
        recession  = final_distance    > midpoint_distance
        bits_ok    = final_bit_count   == _DYN_INITIAL_BITS
        objects_ok = final_object_count == _DYN_INITIAL_OBJECTS

        metrics["approach"]   = bool(approach)
        metrics["recession"]  = bool(recession)
        metrics["bits_ok"]    = bool(bits_ok)
        metrics["objects_ok"] = bool(objects_ok)

        fitness = 1.0 if (approach and recession and bits_ok and objects_ok) else 0.0
        metrics["fitness"] = float(fitness)
        return metrics

    @staticmethod
    def _fail(metrics: dict) -> dict:
        metrics.setdefault("approach", False)
        metrics.setdefault("recession", False)
        metrics.setdefault("bits_ok", False)
        metrics.setdefault("objects_ok", False)
        metrics["fitness"] = 0.0
        return metrics

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── StagedCollisionFitness ──────────────────────────────────────────────────

# 128x128 grid with two 3-bit L-trominos on a collision course.
_STAGED_GRID_SIZE = 128
_STAGED_OBJECT_A = [(60, 40), (61, 40), (60, 41)]
_STAGED_OBJECT_B = [(67, 87), (68, 87), (67, 88)]
_STAGED_INITIAL_BITS = len(_STAGED_OBJECT_A) + len(_STAGED_OBJECT_B)  # 6

# 8-connectivity so diagonally-adjacent cells of an L-tromino count as one object.
_STAGED_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)

_STAGED_MARGIN = 1.0


def _make_staged_grid(grid_size: int = _STAGED_GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _STAGED_OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _STAGED_OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


def _staged_two_object_com_distance(grid: np.ndarray) -> float | None:
    """Return Euclidean distance between the two largest component COMs, or None if < 2."""
    labels, n = label(grid, structure=_STAGED_LABEL_STRUCTURE)
    if n < 2:
        return None
    sizes = sorted(
        ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2 = [sizes[0][0], sizes[1][0]]
    coms = center_of_mass(grid, labels, top2)
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


class StagedCollisionFitness:
    """Fitness function providing a continuous gradient for two-body collisions.

    Two 3-bit L-trominos are placed on a 128x128 toroidal grid. The simulation
    runs for ``horizon`` steps (default 400), capturing snapshots at step 0
    (t_initial), ``midpoint`` (default 200, t_mid), and ``horizon`` (t_final).

    Scoring:
      - Bit conservation is verified at t_mid and t_final against t_initial.
        Any violation immediately returns fitness 0.0.
      - approach_score  = 1.0 if d_mid   < d_initial - MARGIN, else 0.0
      - recession_score = 1.0 if d_final > d_mid     + MARGIN, else 0.0
      - fitness = approach_score + recession_score  (0.0, 1.0, or 2.0)

    This staged scoring creates a clear fitness gradient: rules that merely
    bring particles together score 1.0, while a full approach-then-recede
    sequence scores 2.0.
    """

    name = "StagedCollisionFitness"

    def __init__(
        self,
        horizon: int = 400,
        midpoint: int | None = None,
        grid_size: int = _STAGED_GRID_SIZE,
        rule: dict | None = None,
    ) -> None:
        self.horizon   = int(horizon)
        self.midpoint  = int(midpoint) if midpoint is not None else self.horizon // 2
        self.grid_size = int(grid_size)
        self.rule      = rule

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("StagedCollisionFitness: no rule supplied")

        lut           = rule_dict_to_lut(rule_dict)
        grid          = _make_staged_grid(self.grid_size)
        grid_initial  = grid.copy()
        initial_bits  = int(grid_initial.sum())
        grid_mid      = None

        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == self.midpoint:
                grid_mid = grid.copy()

        if grid_mid is None:
            grid_mid = grid_initial.copy()

        grid_final = grid

        # Bit conservation check — fail fast on any violation.
        mid_bits   = int(grid_mid.sum())
        final_bits = int(grid_final.sum())
        if mid_bits != initial_bits or final_bits != initial_bits:
            return {
                "fitness":         0.0,
                "approach_score":  0.0,
                "recession_score": 0.0,
                "d_initial":       None,
                "d_mid":           None,
                "d_final":         None,
                "initial_bits":    initial_bits,
                "mid_bits":        mid_bits,
                "final_bits":      final_bits,
                "bits_conserved":  False,
            }

        d_initial = _staged_two_object_com_distance(grid_initial)
        d_mid     = _staged_two_object_com_distance(grid_mid)
        d_final   = _staged_two_object_com_distance(grid_final)

        # If we cannot identify two objects at any checkpoint, score 0.
        if d_initial is None or d_mid is None or d_final is None:
            return {
                "fitness":         0.0,
                "approach_score":  0.0,
                "recession_score": 0.0,
                "d_initial":       float(d_initial) if d_initial is not None else None,
                "d_mid":           float(d_mid)     if d_mid     is not None else None,
                "d_final":         float(d_final)   if d_final   is not None else None,
                "initial_bits":    initial_bits,
                "mid_bits":        mid_bits,
                "final_bits":      final_bits,
                "bits_conserved":  True,
            }

        approach_score  = 1.0 if d_mid   < d_initial - _STAGED_MARGIN else 0.0
        recession_score = 1.0 if d_final > d_mid     + _STAGED_MARGIN else 0.0
        fitness         = approach_score + recession_score

        return {
            "fitness":         float(fitness),
            "approach_score":  float(approach_score),
            "recession_score": float(recession_score),
            "d_initial":       float(d_initial),
            "d_mid":           float(d_mid),
            "d_final":         float(d_final),
            "initial_bits":    initial_bits,
            "mid_bits":        mid_bits,
            "final_bits":      final_bits,
            "bits_conserved":  True,
        }

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── LeakyConservationCollisionFitness ──────────────────────────────────────────


class LeakyConservationCollisionFitness:
    """Fitness combining staged motion scoring with a soft bit-conservation penalty.

    Computes a ``staged_score`` using the same approach/recession logic as
    ``StagedCollisionFitness``, but instead of hard-failing on bit-count
    violations applies a continuous penalty:

        fitness = staged_score / (1.0 + bit_error)

    where ``bit_error = abs(final_bits - initial_bits)``.

    Rules with perfect motion but imperfect conservation receive a fractional
    score, preserving evolutionary gradient toward both goals simultaneously.
    """

    name = "LeakyConservationCollisionFitness"

    def __init__(
        self,
        horizon: int = 400,
        midpoint: int | None = None,
        grid_size: int = _STAGED_GRID_SIZE,
        rule: dict | None = None,
    ) -> None:
        self.horizon   = int(horizon)
        self.midpoint  = int(midpoint) if midpoint is not None else self.horizon // 2
        self.grid_size = int(grid_size)
        self.rule      = rule

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("LeakyConservationCollisionFitness: no rule supplied")

        lut          = rule_dict_to_lut(rule_dict)
        grid         = _make_staged_grid(self.grid_size)
        grid_initial = grid.copy()
        initial_bits = int(grid_initial.sum())
        grid_mid     = None

        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == self.midpoint:
                grid_mid = grid.copy()

        if grid_mid is None:
            grid_mid = grid_initial.copy()

        grid_final = grid
        mid_bits   = int(grid_mid.sum())
        final_bits = int(grid_final.sum())
        bit_error  = abs(final_bits - initial_bits)

        d_initial = _staged_two_object_com_distance(grid_initial)
        d_mid     = _staged_two_object_com_distance(grid_mid)
        d_final   = _staged_two_object_com_distance(grid_final)

        if d_initial is None or d_mid is None or d_final is None:
            approach_score  = 0.0
            recession_score = 0.0
        else:
            approach_score  = 1.0 if d_mid   < d_initial - _STAGED_MARGIN else 0.0
            recession_score = 1.0 if d_final > d_mid     + _STAGED_MARGIN else 0.0

        staged_score = approach_score + recession_score
        fitness      = staged_score / (1.0 + bit_error)

        return {
            "fitness":         float(fitness),
            "staged_score":    float(staged_score),
            "approach_score":  float(approach_score),
            "recession_score": float(recession_score),
            "bit_error":       int(bit_error),
            "d_initial":       float(d_initial) if d_initial is not None else None,
            "d_mid":           float(d_mid)     if d_mid     is not None else None,
            "d_final":         float(d_final)   if d_final   is not None else None,
            "initial_bits":    initial_bits,
            "mid_bits":        mid_bits,
            "final_bits":      final_bits,
        }

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── RecessionBiasedFitness ─────────────────────────────────────────────────


class RecessionBiasedFitness(StagedCollisionFitness):
    """Continuous recession scoring with a leaky bit-conservation penalty.

    Runs the full simulation (no midpoint snapshot) and rewards rules that
    first approach then recede.  Recession quality is scored continuously:

        recession_score = min(1.0, final_distance / initial_distance)
        staged_score    = 1.0 + recession_score   # 1.0 (fusion) → 2.0 (perfect)
        fitness         = staged_score / (1.0 + bit_error)

    Approach detection uses the same threshold as the parent class:
    the minimum inter-object distance observed during the simulation must
    fall below ``initial_distance - _STAGED_MARGIN``.  If it does not,
    fitness is 0.0.
    """

    name = "RecessionBiasedFitness"

    @staticmethod
    def _two_coms_and_distance(grid: np.ndarray):
        """Return ((r1,c1), (r2,c2), distance) for the two largest components,
        or None if fewer than two components are present."""
        labels, n = label(grid, structure=_STAGED_LABEL_STRUCTURE)
        if n < 2:
            return None
        sizes = sorted(
            ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
            key=lambda x: x[1],
            reverse=True,
        )
        top2 = [sizes[0][0], sizes[1][0]]
        coms = center_of_mass(grid, labels, top2)
        (r1, c1), (r2, c2) = coms
        dist = math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)
        return (r1, c1), (r2, c2), dist

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("RecessionBiasedFitness: no rule supplied")

        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_staged_grid(self.grid_size)

        # Initial state
        initial_result = self._two_coms_and_distance(grid)
        if initial_result is None:
            return {"fitness": 0.0, "approach_ok": False}
        initial_com1, initial_com2, initial_distance = initial_result
        initial_bits = int(grid.sum())

        # Run full simulation, tracking the minimum inter-object distance.
        min_distance = initial_distance
        for _ in range(self.horizon):
            grid = step_grid(grid, lut)
            d = _staged_two_object_com_distance(grid)
            if d is not None and d < min_distance:
                min_distance = d

        # Final state
        final_result = self._two_coms_and_distance(grid)
        final_bits   = int(grid.sum())
        bit_error    = abs(initial_bits - final_bits)

        # Approach check — same threshold logic as the parent class.
        approach_ok = min_distance < initial_distance - _STAGED_MARGIN
        if not approach_ok:
            return {
                "fitness":          0.0,
                "approach_ok":      False,
                "min_distance":     float(min_distance),
                "initial_distance": float(initial_distance),
                "final_distance":   None,
                "initial_bits":     initial_bits,
                "final_bits":       final_bits,
                "bit_error":        int(bit_error),
            }

        # final_distance is 0 if the two objects merged (fewer than 2 components).
        if final_result is None:
            final_com1, final_com2, final_distance = None, None, 0.0
        else:
            final_com1, final_com2, final_distance = final_result

        recession_score = min(1.0, final_distance / initial_distance) if initial_distance > 0 else 0.0
        staged_score    = 1.0 + recession_score
        fitness         = staged_score / (1.0 + bit_error)

        return {
            "fitness":          float(fitness),
            "approach_ok":      True,
            "staged_score":     float(staged_score),
            "recession_score":  float(recession_score),
            "min_distance":     float(min_distance),
            "initial_distance": float(initial_distance),
            "final_distance":   float(final_distance),
            "initial_bits":     initial_bits,
            "final_bits":       final_bits,
            "bit_error":        int(bit_error),
        }

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)

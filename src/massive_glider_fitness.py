#!/usr/bin/env python3
"""
massive_glider_fitness.py

MassiveGliderFitness: discovers "massive" gliders — coherently translating
patterns whose speed v satisfies  0 < |v| < 1  (strictly sub-luminal).

Standard v=c gliders (patterns that advance exactly one cell per step along
a cardinal or diagonal direction) are explicitly excluded.  The name
"massive" comes from the special-relativity analogy: a particle with rest
mass cannot reach the speed of light, so it travels at 0 < |v| < c.

Procedure
---------
1. Seed a 128×128 toroidal grid with the T_TROMINO_PARTICLE (4-cell T-shape).
2. Run SETTLE_STEPS (200) steps to allow transient behaviour to die out.
3. Record centre-of-mass (COM) at step 200 and step 300.
   velocity vector  v = (com_300 − com_200) / MEASURE_STEPS
4. Early exits:
   a. speed ≈ 0   → fitness 0  (stationary or pure oscillator)
   b. speed ≈ 1   → fitness 0  (v=c glider; well-studied, not our goal)
5. Continue the simulation to MAX_STEPS (1000).  At every CHECKPOINT_EVERY
   (100) steps, predict the expected COM using the measured velocity and
   compare it to the actual COM.  Count how many predictions lie within
   TOLERANCE cells.
6. Fitness = n_valid_checkpoints + complexity_bonus
   where  complexity_bonus = log(1 + mean_bit_count)  rewards "massive"
   (multi-cell) objects over minimal single-bit v=c photons.
"""

import math

import numpy as np

from evolution import (
    rule_dict_to_lut,
    step_grid,
    center_of_mass,
)

# ---------------------------------------------------------------------------
# Seed particle definition
# ---------------------------------------------------------------------------

# T-tromino (4-cell T-tetromino): offsets are (row_delta, col_delta)
# relative to the grid centre.
#
#   . X .      row offset -1, col offset  0
#   X X X      row offset  0, col offsets -1, 0, +1
#
# This shape is asymmetric under 180-degree rotation (rotating it gives a
# different orientation), which breaks left-right symmetry and makes it a
# useful seed for discovering directional gliders.
T_TROMINO_PARTICLE: list[tuple[int, int]] = [
    (-1,  0),   # top centre
    ( 0, -1),   # bottom left
    ( 0,  0),   # bottom centre
    ( 0,  1),   # bottom right
]

# ---------------------------------------------------------------------------
# Tunable constants
# ---------------------------------------------------------------------------

GRID_SIZE        = 128   # square toroidal grid side length
SETTLE_STEPS     = 200   # burn-in before the first COM measurement
MEASURE_STEPS    = 100   # window used to estimate the velocity vector
MAX_STEPS        = 1000  # total steps before the evaluation ends
CHECKPOINT_EVERY = 100   # verification interval after the measure window
TOLERANCE        = 2.5   # max COM deviation (cells) for a checkpoint to pass

# |speed| within this distance of any integer ≥ 1 is treated as v=c.
# Covers both cardinal (speed 1.0) and diagonal (speed ≈ 1.414) gliders.
_V_C_THRESHOLD = 0.15


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _make_particle_grid(
    particle: list[tuple[int, int]],
    grid_size: int = GRID_SIZE,
) -> np.ndarray:
    """Return a zero grid with *particle* centred at (grid_size//2, grid_size//2)."""
    grid   = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


def _is_vc_speed(speed: float) -> bool:
    """Return True if *speed* is close to a positive integer (v=c glider).

    Tests proximity to 1, 2, … up to ceil(speed)+1 so that both unit-step
    cardinal gliders (speed≈1) and diagonal gliders (speed≈√2≈1.414) are
    caught.
    """
    if speed < _V_C_THRESHOLD:
        return False  # near-zero; handled as "stationary" by the caller
    for n in range(1, int(math.ceil(speed)) + 2):
        if abs(speed - n) < _V_C_THRESHOLD:
            return True
    return False


# ---------------------------------------------------------------------------
# Fitness class
# ---------------------------------------------------------------------------

class BaseFitness:
    """Minimal base class establishing the fitness-evaluation API."""

    name: str = "BaseFitness"

    def evaluate(self, rule_dict: dict) -> dict:
        raise NotImplementedError

    def __call__(self, rule_dict: dict) -> dict:
        return self.evaluate(rule_dict)


class MassiveGliderFitness(BaseFitness):
    """Fitness function that selects for sub-luminal (0 < |v| < 1) gliders.

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid.
    settle_steps : int
        Steps to run before the first COM measurement (transient suppression).
    measure_steps : int
        Steps between the two COM snapshots used to estimate velocity.
    max_steps : int
        Total simulation steps; verification checkpoints span
        [settle+measure+checkpoint_every … max_steps].
    checkpoint_every : int
        Step interval at which the predicted COM is compared to actual COM.
    tolerance : float
        Maximum allowed distance (cells) between predicted and actual COM
        for a checkpoint to count as valid.
    """

    name = "MassiveGliderFitness"

    def __init__(
        self,
        grid_size:        int   = GRID_SIZE,
        settle_steps:     int   = SETTLE_STEPS,
        measure_steps:    int   = MEASURE_STEPS,
        max_steps:        int   = MAX_STEPS,
        checkpoint_every: int   = CHECKPOINT_EVERY,
        tolerance:        float = TOLERANCE,
    ) -> None:
        self.grid_size        = int(grid_size)
        self.settle_steps     = int(settle_steps)
        self.measure_steps    = int(measure_steps)
        self.max_steps        = int(max_steps)
        self.checkpoint_every = int(checkpoint_every)
        self.tolerance        = float(tolerance)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def evaluate(self, rule_dict: dict) -> dict:
        """Evaluate *rule_dict* for massive-glider quality.

        Returns
        -------
        dict
            Always contains ``"fitness"`` (float ≥ 0) plus diagnostic keys:
            ``"n_valid"``, ``"n_checked"``, ``"vr"``, ``"vc"``, ``"speed"``,
            ``"mean_bit_count"``, ``"complexity_bonus"``, ``"reason"``.
        """
        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(T_TROMINO_PARTICLE, self.grid_size)

        step        = 0
        bit_sum     = 0
        bit_samples = 0

        # ---- Phase 1: settling ----------------------------------------
        # Advance SETTLE_STEPS steps so that transient behaviour dies out
        # before we begin measuring velocity.
        while step < self.settle_steps:
            grid = step_grid(grid, lut)
            step += 1

        # First COM snapshot
        com_t0 = center_of_mass(grid)
        bit_sum     += int(grid.sum())
        bit_samples += 1

        # ---- Phase 2: velocity measurement ----------------------------
        # Run MEASURE_STEPS more steps and record the COM again.
        while step < self.settle_steps + self.measure_steps:
            grid = step_grid(grid, lut)
            step += 1

        com_t1 = center_of_mass(grid)
        bit_sum     += int(grid.sum())
        bit_samples += 1

        # Velocity vector in cells-per-step.
        # Dividing displacement by MEASURE_STEPS gives the per-step rate.
        vr    = (com_t1[0] - com_t0[0]) / self.measure_steps
        vc_   = (com_t1[1] - com_t0[1]) / self.measure_steps
        speed = math.sqrt(vr ** 2 + vc_ ** 2)

        # ---- Early exits ----------------------------------------------

        if speed < 1e-6:
            # COM did not move: the pattern is stationary or an oscillator
            # whose net displacement over MEASURE_STEPS is zero.
            return self._zero_result("stationary", bit_sum, bit_samples, vr, vc_)

        if _is_vc_speed(speed):
            # Speed is close to an integer — this is a classic v=c glider.
            # We are not interested in these; return 0 to suppress selection.
            return self._zero_result("v=c glider", bit_sum, bit_samples, vr, vc_)

        # ---- Phase 3: constant-velocity verification ------------------
        # Use the measured velocity to predict the COM at each checkpoint
        # and count how many predictions are within TOLERANCE cells of the
        # actual COM.  A high count means the glider travels at a truly
        # constant, fractional speed for an extended period.
        #
        # Prediction anchor: com_t1 at step (settle_steps + measure_steps).
        predict_origin_step = self.settle_steps + self.measure_steps
        n_valid             = 0
        n_checked           = 0
        next_checkpoint     = predict_origin_step + self.checkpoint_every

        while step < self.max_steps:
            grid = step_grid(grid, lut)
            step += 1
            bit_sum     += int(grid.sum())
            bit_samples += 1

            if step >= next_checkpoint:
                dt     = step - predict_origin_step
                pred_r = com_t1[0] + vr  * dt
                pred_c = com_t1[1] + vc_ * dt
                actual = center_of_mass(grid)
                err    = math.sqrt(
                    (actual[0] - pred_r) ** 2 + (actual[1] - pred_c) ** 2
                )
                n_checked += 1
                if err <= self.tolerance:
                    n_valid += 1
                next_checkpoint += self.checkpoint_every

        mean_bit_count = bit_sum / max(bit_samples, 1)

        # Complexity bonus: log-scale reward for larger, "heavier" patterns.
        # A lonely 1-bit pattern gets bonus ≈ log(2) ≈ 0.69; a 10-bit
        # pattern gets ≈ log(11) ≈ 2.40.  This nudges evolution toward
        # physically "massive" gliders rather than minimal photon-like ones.
        complexity_bonus = math.log(1.0 + mean_bit_count)

        fitness = float(n_valid) + complexity_bonus

        return {
            "fitness":          fitness,
            "n_valid":          n_valid,
            "n_checked":        n_checked,
            "vr":               vr,
            "vc":               vc_,
            "speed":            speed,
            "mean_bit_count":   mean_bit_count,
            "complexity_bonus": complexity_bonus,
            "reason":           "ok",
        }

    # ------------------------------------------------------------------
    # Helper: zero-fitness result with diagnostics
    # ------------------------------------------------------------------

    def _zero_result(
        self,
        reason: str,
        bit_sum: int,
        bit_samples: int,
        vr: float,
        vc_: float,
    ) -> dict:
        mean_bc = bit_sum / max(bit_samples, 1)
        return {
            "fitness":          0.0,
            "n_valid":          0,
            "n_checked":        0,
            "vr":               vr,
            "vc":               vc_,
            "speed":            math.sqrt(vr ** 2 + vc_ ** 2),
            "mean_bit_count":   mean_bc,
            "complexity_bonus": 0.0,
            "reason":           reason,
        }


# ---------------------------------------------------------------------------
# Module-level convenience wrapper (mirrors fitness_stable_velocity.py API)
# ---------------------------------------------------------------------------

_DEFAULT = MassiveGliderFitness()


def evaluate(rule_dict: dict) -> dict:
    """Module-level convenience wrapper for MassiveGliderFitness."""
    return _DEFAULT.evaluate(rule_dict)

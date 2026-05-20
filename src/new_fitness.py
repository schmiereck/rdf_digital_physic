#!/usr/bin/env python3
"""
new_fitness.py

DisplacementConsistencyFitness
------------------------------
A fitness function designed to reward consistent, directional motion and
penalize stationary or oscillating "drifter" objects in v<c glider discovery.

The "drifter" exploit
~~~~~~~~~~~~~~~~~~~~~
In cellular-automaton glider searches, evolution can converge on a class of
objects sometimes called *drifters*: particles that do not travel coherently
but instead undergo small periodic oscillations in place (stationary
drifters) or drift through the grid via random-walk behaviour (thermal
drifters).

Such objects exhibit the following characteristics:

  * They occupy a small area (small bounding box) — satisfying bounding-box
    penalties.
  * They preserve their bit count throughout the simulation — satisfying
    bit-conservation gates.
  * Their centre of mass may drift slowly over long distances, but their
    *velocity vectors* change direction unpredictably from one time window
    to the next.

Classic displacement-based fitness metrics (net displacement, cumulative
distance) can be gamed by such drifters because they accumulate large total
distances through random-walk excursions, even though the motion is not
directional or coherent.

How this fitness function defeats drifters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
By dividing the simulation into multiple time windows and computing a
velocity vector for each window, then measuring the *standard deviation* of
those velocity magnitudes, this metric creates a clear separation:

  * A true v<c glider exhibits near-identical velocity vectors in every
    window — its direction and speed are stable. This produces a **low
    standard deviation**.
  * A drifter exhibits wildly varying velocity vectors — its direction and
    speed fluctuate. This produces a **high standard deviation**.

The core fitness formula:

    fitness = mean_velocity_magnitude / (1 + std_dev_velocity_magnitudes)

  * The numerator rewards high average speed across all windows.
  * The denominator (1 + std_dev) suppresses fitness when velocities
    are inconsistent, regardless of how large the mean velocity happens
    to be.

Together with the "leaky" bit-conservation multiplier from LeakyCheckpointFitness,
this creates a robust score that only rewards objects that are simultaneously:

  1. Moving consistently in one direction (low std dev of windowed velocities).
  2. Preserving their mass (bit count) throughout the simulation.

Parameters
----------
num_windows : int
    Number of time windows to divide the simulation into. Default 5.
    More windows give finer-grained detection of velocity fluctuations.
bits_per_cell : int
    Bits per cell (used for future multi-bit extensions). Default 1.

Calling convention
------------------
    fitness_fn = DisplacementConsistencyFitness(num_windows=5)
    score = fitness_fn(sim_history)

    sim_history : list of dict
        Each dict must contain:
          - 'step'    : int — simulation step index
          - 'com'     : tuple[float, float] — centre of mass (row, col)
          - 'bit_count': int   — live cell count at that step
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


class DisplacementConsistencyFitness:
    """Fitness function that rewards consistent, directional motion.

    This fitness function defeats the *drifter* exploit by analysing the
    consistency of velocity across multiple time windows of a simulation.

    Design rationale
    ----------------
    The drifter exploit occurs when a cellular-automaton object exhibits
    random-walk or oscillating behaviour with occasional long displacements.
    Such objects may achieve high cumulative displacement but their motion
    is *inconsistent* — they change direction frequently or oscillate in
    place.

    By dividing the simulation into windows and computing per-window velocity
    vectors, then measuring the standard deviation of velocity magnitudes,
    we create a metric where:

      - True gliders (consistent directional motion) have **low** std dev
        → high fitness.
      - Drifters (inconsistent / oscillating motion) have **high** std dev
        → low fitness, even if their mean velocity is moderate.
      - Stationary objects have near-zero velocity in every window
        → near-zero fitness.

    Scoring pipeline
    ----------------
    1. Divide ``sim_history`` into ``num_windows`` equal-duration windows.
    2. For each window, compute the displacement vector (ΔCOM) and its
       magnitude (velocity proxy, since all windows are equal length).
    3. Compute the mean of the per-window velocity *vectors* (not just
       magnitudes) — this gives the net directional drift.
    4. Compute the standard deviation of the per-window velocity *magnitudes*
       — this measures consistency of motion speed.
    5. Apply the core formula::

           base_fitness = mean_velocity_magnitude / (1 + std_dev_velocity_magnitudes)

       A perfectly consistent glider has std_dev ≈ 0, so
       base_fitness ≈ mean_velocity_magnitude.
       A drifter with the same mean but high std_dev gets heavily penalised.

    6. Multiply by the "leaky" bit-conservation score to enforce mass
       conservation (see ``_compute_conservation_score``).

        final_fitness = base_fitness * total_conservation_score

    Parameters
    ----------
    num_windows : int
        Number of windows to divide the simulation into. Default 5.
        At least 2 windows are needed to measure velocity consistency.
    bits_per_cell : int
        Bits per cell (reserved for future multi-bit support). Default 1.
    strict_conservation : bool
        If True, any bit count change makes the fitness 0.0.
    max_bit_threshold : int or None
        If specified, any step exceeding this bit count makes the fitness 0.0.

    Attributes
    ----------
    name : str
        Display name for registration purposes.
    """

    name = "DisplacementConsistencyFitness"

    def __init__(
        self,
        num_windows: int = 5,
        bits_per_cell: int = 1,
        strict_conservation: bool = False,
        max_bit_threshold: int | None = None,
    ) -> None:
        """Initialise the fitness function.

        Parameters
        ----------
        num_windows : int
            Number of time windows. Must be >= 2 for meaningful velocity
            consistency measurement.
        bits_per_cell : int
            Bits per cell (reserved).
        strict_conservation : bool
            Whether to enforce perfect, non-leaky mass conservation.
        max_bit_threshold : int, optional
            Maximum allowed bit count at any step.
        """
        self.num_windows = max(2, int(num_windows))
        self.bits_per_cell = int(bits_per_cell)
        self.strict_conservation = strict_conservation
        self.max_bit_threshold = max_bit_threshold

    def __call__(
        self,
        sim_history: list[dict[str, Any]],
    ) -> float:
        """Compute fitness score from a simulation history.

        Parameters
        ----------
        sim_history : list of dict
            Simulation history recorded at various steps. Each element
            must be a dict with the following keys:

            - ``'step'`` : int — simulation step index (0-based).
            - ``'com'``  : tuple[float, float] — centre of mass (row, col).
            - ``'bit_count'`` : int — number of live cells at that step.

            The history should be ordered chronologically (though the method
            sorts internally for safety).

        Returns
        -------
        float
            Final fitness score. A score of 0.0 is returned when the
            history is empty, when the simulation runs for zero steps,
            or when there is no net displacement.

        Examples
        --------
        >>> sim_history = [
        ...     {"step": 0,  "com": (64.0, 64.0),  "bit_count": 3},
        ...     {"step": 50, "com": (60.0, 60.5),  "bit_count": 3},
        ...     {"step": 100,"com": (56.0, 57.0),  "bit_count": 3},
        ...     {"step": 150,"com": (52.0, 53.5),  "bit_count": 3},
        ...     {"step": 200,"com": (48.0, 50.0),  "bit_count": 3},
        ...     {"step": 250,"com": (44.0, 46.5),  "bit_count": 3},
        ... ]
        >>> fitness = DisplacementConsistencyFitness(num_windows=5)(sim_history)
        """
        if not sim_history:
            return 0.0

        # ------------------------------------------------------------------
        # 1. Sort by step (defensive — history should be ordered but
        #    we sort to be safe)
        # ------------------------------------------------------------------
        sorted_history = sorted(sim_history, key=lambda e: e["step"])

        if self.max_bit_threshold is not None:
            if any(entry["bit_count"] > self.max_bit_threshold for entry in sorted_history):
                return 0.0

        if self.strict_conservation:
            initial_bits = sorted_history[0]["bit_count"]
            if any(entry["bit_count"] != initial_bits for entry in sorted_history):
                return 0.0

        initial_step = float(sorted_history[0]["step"])
        final_step = float(sorted_history[-1]["step"])
        total_steps = final_step - initial_step

        if total_steps <= 0:
            return 0.0

        # ------------------------------------------------------------------
        # 2. Compute per-window velocity vectors
        # ------------------------------------------------------------------
        steps_per_window = total_steps / self.num_windows

        window_velocity_mags: list[float] = []
        window_velocity_vectors: list[tuple[float, float]] = []

        for w in range(self.num_windows):
            window_start = initial_step + w * steps_per_window
            window_end = window_start + steps_per_window

            # Find the first and last entries in this window's step range.
            # The history is sorted, so we iterate and break early for
            # efficiency once we pass the window boundary.
            first_entry: dict | None = None
            last_entry: dict | None = None

            for entry in sorted_history:
                s = float(entry["step"])

                # Skip entries before this window
                if s < window_start:
                    continue

                # Stop processing once we're past this window's end
                # (the very last entry of the global history belongs to
                #  the last window only, so we clamp window_end to
                #  final_step for the final window to avoid excluding it).
                effective_window_end = window_end
                if w == self.num_windows - 1:
                    effective_window_end = final_step

                if s > effective_window_end:
                    break

                # This entry falls within the current window.
                if first_entry is None:
                    first_entry = entry
                last_entry = entry  # overwrite on every match → last one wins

            if first_entry is None or last_entry is None:
                # No data points in this window — zero velocity.
                window_velocity_mags.append(0.0)
                window_velocity_vectors.append((0.0, 0.0))
                continue

            dx = last_entry["com"][0] - first_entry["com"][0]
            dy = last_entry["com"][1] - first_entry["com"][1]
            velocity_mag = math.sqrt(dx * dx + dy * dy)

            window_velocity_mags.append(velocity_mag)
            window_velocity_vectors.append((dx, dy))

        # ------------------------------------------------------------------
        # 3. Calculate mean of windowed velocity vectors (directional drift)
        # ------------------------------------------------------------------
        mean_dx = sum(v[0] for v in window_velocity_vectors) / self.num_windows
        mean_dy = sum(v[1] for v in window_velocity_vectors) / self.num_windows
        mean_velocity_magnitude = math.sqrt(
            mean_dx * mean_dx + mean_dy * mean_dy
        )

        # ------------------------------------------------------------------
        # 4. Calculate standard deviation of windowed velocity magnitudes
        # ------------------------------------------------------------------
        velocity_magnitudes = np.array(window_velocity_mags, dtype=np.float64)
        std_dev_velocity_magnitudes = float(np.std(velocity_magnitudes))

        # ------------------------------------------------------------------
        # 5. Core fitness formula
        # ------------------------------------------------------------------
        if mean_velocity_magnitude == 0.0:
            # No net directional displacement — nothing to reward.
            base_fitness = 0.0
        else:
            # Standard formula: mean velocity / (1 + std dev of magnitudes).
            # The "+1" in the denominator prevents division by zero when
            # std_dev is also zero (perfect consistency).
            base_fitness = mean_velocity_magnitude / (
                1.0 + std_dev_velocity_magnitudes
            )

        # ------------------------------------------------------------------
        # 6. Leaky bit-conservation score (from LeakyCheckpointFitness)
        # ------------------------------------------------------------------
        total_conservation_score = self._compute_conservation_score(
            sorted_history
        )

        # ------------------------------------------------------------------
        # 7. Final fitness: consistency score × conservation score
        # ------------------------------------------------------------------
        fitness = base_fitness * total_conservation_score

        return float(fitness)

    # ── Private helpers ────────────────────────────────────────────────────

    def _compute_conservation_score(
        self, sim_history: list[dict[str, Any]]
    ) -> float:
        """Compute the 'leaky' bit-conservation score from simulation history.

        This mirrors the conservation scoring logic from
        ``LeakySubLightFitness`` in ``leaky_fitness.py``.  Instead of hard-
        failing on bit-count changes, it applies a continuous penalty factor
        proportional to how closely the particle's mass tracks the original
        mass.

        For each step *i* in the history:

            if bit_count[i] == initial_bit_count:
                conservation_factor[i] = 1.0
            else:
                conservation_factor[i] = min(bit_count[i], initial_bits)
                                         / max(bit_count[i], initial_bits)

        The total conservation score is the mean of all per-step factors.

        Parameters
        ----------
        sim_history : list of dict
            Sorted simulation history (must contain ``'bit_count'`` keys).

        Returns
        -------
        float
            Conservation score in the range [0, 1]. A value of 1.0 means
            perfect bit-count conservation throughout the simulation.
            Lower values indicate bit loss or gain.

        Why "leaky" ?
        -------------
        Unlike ``CheckpointFitness``, which hard-fails on any bit-count
        change at a checkpoint, the leaky variant applies a *fractional*
        penalty.  This preserves evolutionary gradient: a rule that gains
        or loses a few bits still earns partial fitness, guiding evolution
        toward perfect conservation rather than rejecting the candidate
        outright.
        """
        if not sim_history:
            return 1.0

        initial_bits = sim_history[0]["bit_count"]

        # Guard against degenerate empty particle.
        if initial_bits == 0:
            return 1.0

        conservation_factors: list[float] = []
        for entry in sim_history:
            bit_count = entry["bit_count"]
            if bit_count == initial_bits:
                conservation_factors.append(1.0)
            else:
                # Fractional penalty: closer to 1.0 when bit_count is close
                # to initial_bits, approaching 0 as it diverges.
                conservation_factors.append(
                    min(bit_count, initial_bits)
                    / max(bit_count, initial_bits)
                )

        total_conservation_score = sum(conservation_factors) / len(
            conservation_factors
        )
        return float(total_conservation_score)

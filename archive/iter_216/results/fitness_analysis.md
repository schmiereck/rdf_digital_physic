# Fitness Function Analysis: Why `LateWindowDisplacementFitness` Selects for v=1c

## 1. Background

The iter_215 evolutionary search used `LateWindowDisplacementFitness` from
`src/fitness_v_lessthan_c.py` with the intent of finding sub-light-speed (v<c)
particles. The resulting champion rule was characterised in iter_216.2 and found
to be a **speed-of-light glider (v=1c)**: the centre-of-mass moves exactly
−1.0 row per step with no column drift and no internal oscillation.

Measured evidence from `archive/iter_216/results/characterization.json`
(256×256 grid, 500 steps):

| metric | value |
|--------|-------|
| CoM at step 250 | (−121.667, 128.667) |
| CoM at step 500 | (−371.667, 128.667) |
| net displacement (250→500) | 250.0 cells |
| avg_velocity_row | −1.000 cells/step |
| avg_velocity_magnitude | **1.000 cells/step** |

Every recorded step in the 500-entry step log shows a CoM shift of exactly
−1/step, with no variation — the signature of a trivially periodic (period = 1)
glider at the lattice speed limit.

---

## 2. Root Cause: Why `LateWindowDisplacementFitness` Rewards v=1c

### 2.1 The Fitness Formula

```python
fitness = late_window_displacement / (1 + final_bb_area)
```

`late_window_displacement` is the Euclidean distance between the (wrapped)
centre-of-mass at `window_start` (step 200 in iter_215) and `window_end`
(step 400). The bounding-box area penalises diffuse patterns.

### 2.2 The Speed Proportionality Problem

For a compact particle (constant `bb_area = b`) moving at speed `s` cells/step
over a window of `W` steps:

```
fitness ≈ (s × W) / (1 + b)
```

This is **directly proportional to speed**. The fastest possible compact
particle — a v=1c glider — maximises fitness at:

```
fitness_max ≈ W / (1 + b)
```

Any v<c glider with speed s = 1/k (one cell every k steps) yields:

```
fitness(v<c) = fitness_max / k
```

So a period-4 glider (k=4, v=0.25c) earns only one-quarter the fitness of the
equivalent v=1c glider. The fitness function has **no ceiling on speed** and
thus naturally drives evolution toward the speed-of-light limit.

### 2.3 The Toroidal CoM Wrapping Artefact

`LateWindowDisplacementFitness` uses the raw `center_of_mass` function, which
computes the naive mean of live-cell coordinates on the toroidal grid. When a
v=1c glider traverses the grid boundary during the measurement window, the
wrapped CoM can jump discontinuously, producing an *apparent* displacement much
smaller than the true travelled distance.

In iter_215 (128×128 grid, window [200, 400]):

- True displacement: 200 cells (1 cell/step × 200 steps)
- Measured (`late_window_displacement`): 12 cells
- Because 200 mod 128 = 72, and the CoM wraps discontinuously around the boundary

Despite the wrapping artefact compressing the measured displacement, the v=1c
glider still won because no v<c candidate achieved comparable compactness and
sustained motion. The wrapping artefact partly *concealed* the true speed, but
did not prevent convergence to v=c.

### 2.4 Why v=1c Has No Structural Barrier

A v=1c glider has **period T = 1**: the pattern at step t+1 is identical to the
pattern at step t, shifted by exactly one lattice unit. No internal state
changes are required. This is the *simplest possible persistent glider* and
therefore the easiest to evolve.

A v<c glider with speed 1/k must have period T = k: the particle passes through
k distinct internal configurations before returning to its original shape
(displaced by 1 cell). A period-4 v=0.25c glider requires four distinct states
to co-exist in a stable cycle. This is structurally more complex and
exponentially harder to evolve without explicit fitness incentives.

`LateWindowDisplacementFitness` provides *no incentive* to discover this
complexity — it penalises it indirectly by producing lower displacement scores.

---

## 3. Key Signatures That Distinguish v<c from v=1c

| Property | v=1c glider | v<c glider (period k) |
|----------|-------------|----------------------|
| CoM shift per step | constant = 1 | mean = 1/k, oscillates |
| Internal period (T) | 1 | k > 1 |
| CoM velocity variance | 0 | > 0 (oscillates around mean) |
| Cell-configuration period | 1 | k |
| Displacement over W steps | W | W/k |

The most reliable diagnostic for v<c is **internal period > 1**. A v<c glider
*must* cycle through more than one configuration per net displacement step.
Concretely:

- A "1/2-c glider" (period 2): even steps show configuration A, odd steps show
  configuration B (shifted A). Two states per cell advance.
- A "1/4-c glider" (period 4): four states A→B→C→D→A (shifted A). Four states
  per cell advance.

A v=1c glider has period 1: configuration at step t equals configuration at
step t−1 shifted by 1 cell. No oscillation.

---

## 4. Proposed New Fitness Function: `SubLightFitness`

### 4.1 Design Principles

The new function must:

1. **Reward motion** — zero fitness for stationary patterns.
2. **Penalise v=1c** — zero or near-zero fitness for particles moving at speed ≥ threshold.
3. **Reward internal oscillation** — higher period → higher bonus, to select for the internal structure that v<c gliders require.
4. **Remain compact** — bounding-box penalty unchanged.
5. **Enforce bit conservation** — hard gate, unchanged.

### 4.2 Metrics to Compute

**Metric 1: Late-window displacement** (existing)
```
displacement = |CoM(window_end) - CoM(window_start)|
```
Use unwrapped (cumulative) CoM tracking to avoid the toroidal artefact.

**Metric 2: Measured velocity**
```
measured_velocity = displacement / (window_end - window_start)
```

**Metric 3: Internal period T**

Sample the particle's *normalised configuration* — the sorted list of
(Δrow, Δcol) offsets of all live cells from the CoM — at each step in a
detection window (e.g., steps 600–800, well after settling). Scan for the
smallest k such that `config(t) == config(t + k)`. Cap the search at
`max_period` (e.g., 64).

If no period is found within the cap, assume the pattern is chaotic (period = 0
→ fitness = 0).

**Metric 4: Bounding-box area** (existing)

### 4.3 Fitness Formula

```
if not bit_conserved:                 return 0.0
if displacement == 0:                 return 0.0
if measured_velocity >= v_threshold:  return 0.0   # hard reject v=c
if period <= 1:                       return 0.0   # hard reject trivial period

period_bonus = 1.0 - (1.0 / period)  # 0 for T=1, 0.5 for T=2, 0.75 for T=4, ...
fitness = (displacement / (1 + bb_area)) * period_bonus
```

Properties of this formula:

| Particle type | displacement | period | period_bonus | fitness |
|---------------|-------------|--------|--------------|---------|
| Stationary oscillator | 0 | k | any | **0** |
| v=1c glider | W | 1 | 0 | **0** |
| v=0.5c glider, compact | W/2 | 2 | 0.5 | W/4 / (1+b) |
| v=0.25c glider, compact | W/4 | 4 | 0.75 | 3W/16 / (1+b) |
| Chaotic puffer | >0 | 0 | — | **0** |

The fitness is maximised at intermediate speeds, with no explicit velocity
target. The `period_bonus` term grows as k increases, partially compensating the
lower displacement, so slower particles are not totally disadvantaged.

### 4.4 Implementation Sketch

```python
class SubLightFitness:
    """Fitness that explicitly rewards sub-light-speed periodic particles."""

    name = "SubLightFitness"

    def __init__(
        self,
        grid_size:        int   = 128,
        simulation_steps: int   = 1200,
        window_start:     int   = 600,
        window_end:       int   = 1000,
        period_window_start: int = 600,
        period_window_end:   int = 800,
        max_period:       int   = 64,
        v_threshold:      float = 0.9,
        particle:         list | None = None,
        expected_bits:    int   = 3,
    ) -> None: ...

    def _detect_period(self, grid_history: list[np.ndarray], start: int, end: int, max_k: int) -> int:
        """Return smallest k where config(t+k) == config(t) for t in [start, end-k].
        
        Normalised config = frozenset of (Δr, Δc) offsets from CoM.
        Returns 0 if no period found within max_k.
        """
        configs = []
        for grid in grid_history[start:end]:
            com = center_of_mass(grid)
            positions = set(zip(*np.where(grid > 0)))
            norm = frozenset((r - round(com[0]), c - round(com[1])) for r, c in positions)
            configs.append(norm)

        for k in range(1, max_k + 1):
            if all(configs[i] == configs[i + k] for i in range(len(configs) - k)):
                return k
        return 0

    def evaluate(self, rule_dict: dict) -> dict:
        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(self.particle, self.grid_size)

        initial_bits = int(grid.sum())
        grid_history = [grid.copy()]
        com_history  = [center_of_mass(grid)]  # unwrapped CoM tracking

        # Simulate, storing history
        cum_offset = np.array([0.0, 0.0])
        prev_raw_com = np.array(center_of_mass(grid))

        for _ in range(self.simulation_steps):
            grid = step_grid(grid, lut)
            raw_com = np.array(center_of_mass(grid))
            # Unwrap: detect jumps larger than half the grid (toroidal wrap)
            delta = raw_com - prev_raw_com
            delta -= np.round(delta / self.grid_size) * self.grid_size
            cum_offset += delta
            prev_raw_com = raw_com
            com_history.append(cum_offset.copy() + np.array(center_of_mass(
                _make_particle_grid(self.particle, self.grid_size))))
            grid_history.append(grid.copy())

        final_bits = int(grid.sum())

        # Bit-conservation gate
        if initial_bits != self.expected_bits or final_bits != self.expected_bits:
            return {"fitness": 0.0, "reason": "bit_conservation_failed", ...}

        # Late-window displacement (using unwrapped CoM)
        com_start = com_history[self.window_start]
        com_end   = com_history[self.window_end]
        dx = com_end[0] - com_start[0]
        dy = com_end[1] - com_start[1]
        displacement = math.sqrt(dx*dx + dy*dy)
        window_steps = self.window_end - self.window_start
        measured_velocity = displacement / window_steps if window_steps > 0 else 0.0

        if displacement == 0.0:
            return {"fitness": 0.0, "reason": "no_displacement", ...}
        if measured_velocity >= self.v_threshold:
            return {"fitness": 0.0, "reason": "velocity_at_c", ...}

        # Period detection
        period = self._detect_period(
            grid_history, self.period_window_start, self.period_window_end, self.max_period
        )
        if period <= 1:
            return {"fitness": 0.0, "reason": "period_too_short", ...}

        # Bounding box (final state)
        bb_area = _bounding_box_area(grid)

        # Combined score
        period_bonus = 1.0 - 1.0 / period
        fitness = (displacement / (1.0 + bb_area)) * period_bonus

        return {
            "fitness":            fitness,
            "reason":             "ok",
            "displacement":       displacement,
            "measured_velocity":  measured_velocity,
            "period":             period,
            "period_bonus":       period_bonus,
            "bb_area":            bb_area,
            ...
        }
```

### 4.5 Important Implementation Note: Unwrapped CoM

The existing `center_of_mass` function computes a naive average of cell
coordinates, which is discontinuous when particles cross the toroidal boundary.
`SubLightFitness` must track CoM cumulatively by integrating the *delta* between
consecutive steps and correcting for grid-wrap jumps (any delta larger than
grid_size/2 in magnitude is a wrap). This gives an unwrapped displacement that
correctly measures the true distance travelled, even across multiple grid
traversals.

### 4.6 Parameter Guidance

| Parameter | Suggested value | Rationale |
|-----------|-----------------|-----------|
| `simulation_steps` | 1200 | Enough for settling + long window |
| `window_start / end` | 600 / 1000 | Skip transients; 400-step window |
| `period_window` | 600 / 800 | Overlapping with displacement window |
| `max_period` | 64 | Detects up to 1/64-c speed |
| `v_threshold` | 0.9 | Hard-reject v ≥ 0.9c |

---

## 5. Summary

| Aspect | `LateWindowDisplacementFitness` (old) | `SubLightFitness` (proposed) |
|--------|--------------------------------------|------------------------------|
| v=1c glider | Rewarded (maximum displacement) | Rejected (period ≤ 1, v ≥ threshold) |
| v<c glider | Penalised by lower displacement | Rewarded by period_bonus × displacement |
| Stationary oscillator | Rejected (zero displacement) | Rejected (zero displacement) |
| Chaotic puffer | Suppressed by bb_area | Suppressed by bb_area + period=0 gate |
| Toroidal wrap | Artefact compresses measurement | Fixed by unwrapped CoM tracking |

The root cause of the iter_215/216 mislabelling is geometric: `fitness ∝ speed`
with no speed ceiling. `SubLightFitness` breaks this proportionality by
introducing a hard velocity gate and a period bonus that makes internal
oscillation directly fitness-relevant for the first time.

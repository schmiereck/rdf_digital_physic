# Current Research State
Phase: v<c Search Exploit Identified

## Goal
Discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- The platform is stable. The root cause of previous execution errors was an incorrect import statement, which has been fixed and verified (`iter_213.8`, `iter_213.9`).
- The `NetDisplacementFitness` function, designed to defeat "puffer" and "oscillator" exploits, is vulnerable to a new "transient drift" exploit. A pattern can achieve a non-zero fitness score by shifting its center-of-mass during an initial settling phase without any subsequent, sustained motion (`iter_213.10`).

## Refuted
- The champion rule discovered in `iter_213.10` does not produce a `v<c` glider. It produces a compact oscillator.

## Open Questions
- How can a fitness function be designed to reward *sustained* motion while ignoring initial, transient settling effects?
- Is measuring displacement over a later window (e.g., steps 500-1000) sufficient to defeat the "transient drift" exploit?
- Could a metric based on velocity consistency be more robust?

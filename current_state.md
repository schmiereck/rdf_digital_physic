Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- Formal search for simple gliders from small seeds has failed across numerous rule classes (C6/C2 symmetry, conserving/non-conserving) (iter_006-081).
- Evolutionary search using abstract complexity or simple stability as a fitness metric is ineffective, evolving chaotic or annihilating rules respectively (iter_082-089).
- A "primordial soup" evaluation is a valid method for identifying rules that create structure from chaos (iter_105).
- "Cooling" rules, with a bias for mapping higher-density states to lower-density ones, successfully resolve a chaotic soup into low-density, persistent, structured states (iter_105). We have four such rules.

## Refuted
- Simple, contiguous initial seeds are not a reliable source of gliders for the rule spaces explored.
- Abstract complexity and simple stability are poor proxy metrics for glider-supporting behavior.

## Current Best Result
We have identified four C2-symmetric "cooling" rules that reliably create a sparse "ash" of complex objects from a dense, random soup (iter_105).

## Open Questions
- Does the "ash" from cooling rules contain stable, moving particles (gliders)?
- What are the properties of any emergent gliders found?
- Are these gliders common across all four cooling rules?
- Can emergent gliders interact in a non-trivial way?

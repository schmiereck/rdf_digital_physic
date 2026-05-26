Update the file src/pre_registration.md to add the following SRM-mandated framing at the top of the document, right after the title line. Insert this text:

**FEASIBILITY BENCHMARK CLASSIFICATION:** This experiment is a non-physical topological feasibility study. It relaxes bit conservation (a core axiom of the LGCA framework) to test whether the 3D FCC lattice geometry can support cooperative-survival gliders AT ALL when conservation is relaxed. Any discovered glider will serve as a kinematic template only; the ultimate goal remains compiling these behaviors back into a reversible, bit-conserving framework (such as a multi-site block-partition CA). This is NOT a physical model.

Also add the following additional exploit-prevention criteria from the SRM to section 2 (Falsification Criterion), as F5 and F6:
- F5: Bloomer Exploit — A candidate is refuted if its bit-count increases monotonically or exceeds 4× the initial seed weight after step 100.
- F6: Debris Cloud — The moving pattern must remain localized within a bounding box of at most 10×10×10 cells after step 100. Patterns shedding static/chaotic debris indefinitely are not clean gliders.

Also update F2 to say "survives ≥50 steps alone" (matching the pre-registration text) rather than "≥100 steps".

Keep all other content unchanged. Write the complete updated file.
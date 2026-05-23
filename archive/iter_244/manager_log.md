# Research Manager Log - Iteration 244

## Iteration 244 -> Manager [Proposed Research Plan]

**Proposed Hypothesis:**
Under the O_h-symmetric, reversible, bit-conserving LUT-08 CA rule on the 3D FCC grid, a CPT-conjugate state of the LUT-08 glider (obtained by time-reversal and spatial reflection) acts as a stable physical antiparticle that propagates in the opposite direction (-v). In a head-on collision with the original glider, they undergo clean mutual annihilation where 100% of the combined 8 bits scatter into independent, non-interacting single-bit states propagating at the vacuum speed of light (v=1c), leaving exactly zero bound states or stationary debris.

**Proposed Falsification Criterion:**
The hypothesis will be refuted if:
1. The constructed antiparticle state is unstable in vacuum (i.e. disperses, alters its bit count, or deviates from constant velocity -v over 100 steps).
2. The chirality and sub-lattice parities of the antiparticle do not satisfy the CPT transformation laws (i.e. the chirality sequence is not the negated and time-reversed sequence of the original glider).
3. The head-on collision leaves any stationary bits (v=0), any bound states of size >= 2 bits, or any particles traveling at sub-light speed (v < 1c) after the interaction region has cleared (t = 80 steps).

**Proposed Method:**
1. Implement a Python script `src/fcc_antiparticle_annihilation.py` to construct the CPT-conjugate (antiparticle) of the LUT-08 glider.
2. Simulate the antiparticle in vacuum for 100 steps on a 64^3 FCC grid to confirm stability, constant velocity, and bit conservation.
3. Compute and track the chirality and sub-lattice parities of the antiparticle to verify CPT symmetry.
4. Set up a head-on collision between the LUT-08 glider and its antiparticle, simulating for 100 steps.
5. Analyze the asymptotic state (t = 80 to 100) to verify that all 8 bits are in independent, non-interacting single-bit channels propagating at v=1c, and that zero stationary or bound-state remnants remain.

---

## Iteration 244 -> Planner [Strategic Guidance]

### Manager's Note: Strategic Guidance for Phase 7.3

#### 1. Construction-vs-Empirical Distinction in CPT Symmetry
You must distinguish between *code verification* and *empirical discovery* in this sub-phase:
* **Vacuum Stability is Constructional:** Because the underlying 3D FCC CA rule is mathematically reversible and O_h-symmetric, any valid glider solution *must* have a stable time-reversed and parity-reversed counterpart. If your constructed "antiparticle" is stable in vacuum, this does **not** count as an emergent physical discovery; it merely verifies that you have implemented the discrete $P$ and $T$ coordinate mapping operators correctly in your Python scripts.
* **Annihilation Dynamics are Empirical:** The rule was not engineered to force mutual annihilation. How the particle and antiparticle interact when their localized bit patterns overlap is a highly non-trivial, empirical test of the rule's non-linear dynamics. 

#### 2. Phase-Space Sweep vs. Hand-Picked Success
Do not search for a single, hand-tuned collision alignment that happens to show "clean annihilation" and declare victory. Because the LUT-08 glider has a periodic internal state, the collision outcome will be highly sensitive to the relative spatial offset (impact parameter) and temporal phase alignment. 
* You must pre-register and execute a systematic phase-space sweep over all relative phase alignments ($\Delta t \in [0, \text{period}-1]$) and minimal transverse offsets.
* If the gliders elastically scatter, form a stationary breather, or produce a different bound state in most channels, report this *honest null result* regarding "clean annihilation" without attempting to alter the underlying rule. A complete map of the interaction cross-section is the required scientific milestone, regardless of whether "annihilation" is the dominant channel.

#### 3. Pre-Registration Mandate
Before executing any simulations, ensure `src/pre_registration.md` is populated with:
1. The exact mathematical definitions of your discrete Parity ($P$) and Time-Reversal ($T$) operators on the 12-channel FCC neighborhood. Note that since time is projected, $T$-reversal within a forward-running spatial CA requires a specific velocity-channel negation and phase alignment.
2. The quantitative falsification criteria, including the exact threshold for what constitutes "clean annihilation" (e.g., zero bound states of size $\ge 2$ bits remaining in the interaction zone after $t=100$ steps).

---


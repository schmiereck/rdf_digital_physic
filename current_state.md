Phase: Strategic Pivot

**Goal:** Evolve or discover C2-symmetric rules that support stable, moving particles (gliders).

**Refuted:**
- The strategy of evolving rules that spontaneously generate gliders from a chaotic, high-density random soup has been falsified. Multiple evolutionary runs with various fitness metrics (`displacement`, `velocity_stability`, `late_displacement`, `composite_fitness`) have failed to produce a viable glider-producing rule. The systems consistently collapse into either explosive growth or static, frozen patterns (iter_091, iter_127, iter_157, iter_166).

**Confirmed:**
- Fitness metrics can be designed to successfully penalize non-viable, explosive rules (iter_156, iter_159).

**Next Steps:**
The "emerge from chaos" approach is declared a dead end. The research will pivot to a "glider nursery" strategy. This involves initializing the simulation grid with a simple, pre-defined particle pattern and evolving rules specifically to propagate and sustain that pattern. This simplifies the search problem from discovering emergence and propagation simultaneously to just discovering propagation.
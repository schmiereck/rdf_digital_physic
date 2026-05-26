Task: Step 1 and Step 2 of the experimental pipeline.

1. Update `src/pre_registration.md` Step 4 to remove the impossible C<->E requirement. Replace with:
"Weight-2 orbit mappings are self-maps only (cross-orbit C↔E and B↔D mappings are mathematically impossible under O_h due to non-conjugate stabilizer subgroups). F5 compliance must be achieved through weight-3+ orbit pairings where rest-channel states map to non-rest-channel states and vice versa."

2. Run the positive control (2D hex glider rule) for 500 steps by executing `python src/experiment_250_hex_decomposition.py` (or writing a simple wrapper/runner if needed) to verify and confirm:
- Binding energy > 0 (single-bit decomposition kills all constituent bits or changes trajectory/velocity, confirming binding energy > 0)
- Cooperative survival active (weight-1 -> 0, i.e., single bit decays to 0)

Provide a summary of the edits made to `src/pre_registration.md` and the stdout/results of running the positive control.
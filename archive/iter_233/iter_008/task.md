Run the existing test suite `python src/test_engine_d4_closed_loop.py` and `python src/test_speed.py` to measure the current speed (steps per second).
Then, modify `src/engine_d4_closed_loop.py` to optimize the latency field update:
1. Remove the expensive `cutoff_radius` dilation loop (which does 24 `np.roll` calls per step).
2. Simply compute the Laplacian and update the entire `latency_field` in one go.
3. Clamp values below `1e-5` to `0.0` (to prevent subnormal underflow and clean up numerical noise).
4. Run the tests again to verify they still pass perfectly and compare the new speed (steps per second). Print the performance speedup.
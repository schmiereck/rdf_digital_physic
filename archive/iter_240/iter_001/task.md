Write a python script `src/profile_sim_speed.py` to measure the execution time of 80 steps of `stream` and `collide` on an L=32 grid.
The script should:
1. Load `stream` and `collide` from `src/engine_3d.py`.
2. Generate a random bijective bit-conserving LUT or load the lut from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Seed a single glider.
4. Run 80 steps of stream and collide on a 32x32x32 grid.
5. Print the time taken for 80 steps, and estimate how many simulations we can run per minute.
Run this script and print the output.
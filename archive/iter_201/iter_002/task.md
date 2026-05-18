The analysis in `201.1` revealed the champion `v<c` glider rule from `iter_200` actually produces a stationary, period-4 oscillator.

Your task is to create a Python script `src/visualize_v_lt_c_object.py` to visualize this behavior.

**Requirements:**

1.  **Load the Rule and Seed:** Load the champion rule from `archive/iter_200/results/champion_v_lt_c_rule.json` and initialize a 128x128 grid with the standard 3-bit L-tromino seed.
2.  **Generate Animation:** Run the simulation for 16 steps to show four full cycles of the period-4 oscillation.
3.  **Create a GIF:** Generate a GIF animation of the process. The view should be zoomed in on the object to clearly show the changing pattern.
4.  **Output:** Save the final animation to `archive/iter_201/results/oscillator.gif`.
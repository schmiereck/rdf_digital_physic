#!/usr/bin/env python3
"""
Script to print the entire DisplacementConsistencyFitness.__call__ method
source code from src/new_fitness.py, so we can see how velocity is calculated
and why a rule with speed ~1.0 was allowed despite max_velocity_threshold=0.9.
"""

import re

# Read the source file
source_path = "src/new_fitness.py"
with open(source_path, "r") as f:
    source = f.read()

lines = source.splitlines()

# Find the __call__ method using regex
call_start = None
call_end = None
indent_level = None

for i, line in enumerate(lines):
    if re.match(r'^\s+def __call__\(', line):
        call_start = i
        indent_level = len(line) - len(line.lstrip())
        continue

    if call_start is not None and call_end is None:
        stripped = line.lstrip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
            current_indent = len(line) - len(stripped)
            if current_indent <= indent_level and (stripped.startswith('def ') or stripped.startswith('class ')):
                call_end = i
                break

if call_end is None:
    call_end = len(lines)

print("=" * 80)
print(f"Source file: {source_path}")
print(f"Method __call__ starts at line {call_start+1}, ends at line {call_end}")
print("=" * 80)
print()

# Print the extracted method
for i in range(call_start, call_end):
    print(f"{i+1:5d} | {lines[i]}")

print()
print("=" * 80)
print()

# Print analysis
print("KEY ANALYSIS")
print("=" * 80)
print()
print("1. PER-WINDOW VELOCITY CALCULATION:")
print("   For each window:")
print("     dx = last_COM[0] - first_COM[0]   (displacement in grid units)")
print("     dy = last_COM[1] - first_COM[1]")
print("     window_steps = last_step - first_step")
print("     velocity_mag = sqrt(dx^2 + dy^2) / window_steps  [cells/step]")
print("     (Also: dx /= window_steps, dy /= window_steps)")
print()
print("2. MEAN VELOCITY VECTOR (AVERAGING ACROSS WINDOWS):")
print("     mean_dx = sum(all_window_dx) / num_windows")
print("     mean_dy = sum(all_window_dy) / num_windows")
print("     mean_velocity_magnitude = sqrt(mean_dx^2 + mean_dy^2)")
print()
print("3. MAX VELOCITY THRESHOLD CHECK:")
print("   if max_velocity_threshold is not None")
print("   and mean_velocity_magnitude >= max_velocity_threshold:")
print("       return 0.0")
print()
print("=" * 80)
print("WHY SPEED ~1.0 MIGHT PASS A 0.9 THRESHOLD")
print("=" * 80)
print()
print("The check uses mean_velocity_magnitude, which is the magnitude of the")
print("AVERAGED velocity VECTOR across all windows -- NOT the mean of per-window")
print("magnitudes. These are mathematically different:")
print()
print("  |E[v]|  vs  E[|v|]")
print()
print("  |E[v]|  = magnitude of average velocity vector (this is what is checked)")
print("  E[|v|]  = average of per-window velocity magnitudes")
print()
print("By triangle inequality:  |E[v]| <= E[|v|]")
print()
print("This means the mean_velocity_magnitude is ALWAYS <= the average of per-window")
print("magnitudes. However, if speed was consistently ~1.0 in the SAME direction")
print("across all windows, then |E[v]| ~ E[|v|] ~ 1.0, and the threshold SHOULD")
print("have blocked it.")
print()
print("HOW CAN ~1.0 SPEED PASS 0.9 THRESHOLD?")
print("  a) The per-window velocity magnitude is NOT actually ~1.0. The COM")
print("     displacement per window might be smaller than expected due to")
print("     how window_start/window_end pick first_entry/last_entry.")
print()
print("  b) max_velocity_threshold was None or set to a different value")
print("     when this particular rule was evaluated.")
print()
print("  c) The COM is unwrapped (handles toroidal wrap-around), so if the")
print("     object moves near grid edges, unwrapped COM displacement could")
print("     differ from what you'd naively expect.")
print()
print("  d) The window's first_entry and last_entry might be close together")
print("     even if the window covers a large step range. For example, if")
print("     no data point falls near the window start/end boundaries, the")
print("     window_steps could be small, inflating velocity_mag. But this")
print("     would make velocity_mag LARGER, not smaller, so this doesn't")
print("     explain why it passes the threshold -- it would make it fail.")
print()
print("  e) MOST LIKELY: The object's COM movement between first_entry and")
print("     last_entry within each window is small compared to the time span.")
print("     If the simulation history has coarse sampling (e.g. only a few")
print("     checkpoints), the first and last data points in a window might")
print("     be close together, giving a velocity based on a tiny displacement")
print("     over a short time -- potentially much less than 1.0 cells/step.")
print()
print("     Example: if a window spans 100 steps but only has data at steps")
print("     50 and 60, the velocity is calculated over 10 steps, not 100.")
print("     If COM moved 0.5 cells in those 10 steps, velocity = 0.05 --")
print("     well below 0.9, even though the object's true speed might be 1.0.")
print()
print("=" * 80)
print("WINDOWING DETAIL")
print("=" * 80)
print()
print("  steps_per_window = total_steps / num_windows")
print("  Window w covers: [initial + w*steps_per_window, initial + (w+1)*steps_per_window]")
print("  velocity = COM_displacement(first_entry to last_entry) / window_span")
print()
print("  KEY: window_steps = last_entry['step'] - first_entry['step']")
print("  This is the ACTUAL step difference between data points in the window,")
print("  NOT the theoretical steps_per_window!")
print()
print("  The velocity magnitude IS divided by window_steps (not steps_per_window),")
print("  so if first_entry and last_entry are close together, velocity_mag gets")
print("  inflated, not deflated. So this alone doesn't explain passing the threshold.")
print()
print("  HOWEVER: the mean_velocity_magnitude is the magnitude of the AVERAGE of")
print("  (dx/window_steps, dy/window_steps) across all windows. If different")
print("  windows have different first/last entries, the per-window velocities")
print("  will vary, and averaging vectors with different directions yields a")
print("  smaller resultant -- possibly below 0.9 even if individual magnitudes")
print("  are around 1.0.")
print("════════════════════════════════════════════════════════════════════════════")

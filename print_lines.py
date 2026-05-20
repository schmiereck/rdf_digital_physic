#!/usr/bin/env python3
"""Print lines 300 to 370 from src/new_fitness.py with line numbers."""

start_line = 300
end_line = 370
filepath = "src/new_fitness.py"

with open(filepath, "r") as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines in {filepath}: {total_lines}\n")
print(f"Printing lines {start_line} to {end_line}:\n")
print("=" * 80)

for i, line in enumerate(lines, start=1):
    if start_line <= i <= end_line:
        # Remove trailing newline for clean display, but keep internal whitespace
        print(f"{i:>4d}: {line}", end="")

print("\n" + "=" * 80)
print(f"\nDone. Printed {end_line - start_line + 1} lines.")

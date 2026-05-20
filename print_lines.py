#!/usr/bin/env python3
"""Print lines 240–285 of src/new_fitness.py with line numbers."""

path = r"src\new_fitness.py"

with open(path, "r") as f:
    all_lines = f.readlines()

for i in range(239, min(285, len(all_lines))):  # 0-based index
    print(f"{i+1:4d} | {all_lines[i]}", end="")

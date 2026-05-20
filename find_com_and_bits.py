#!/usr/bin/env python3
"""Search for 'com_and_bits' definition in run_evolution_exp_221.py and print it."""

from pathlib import Path

FILE_PATH = Path(__file__).parent / "src" / "run_evolution_exp_221.py"

with open(FILE_PATH) as f:
    lines = f.readlines()

# Search for the def line containing 'com_and_bits'
for i, line in enumerate(lines, start=1):
    if "com_and_bits" in line and "def " in line:
        # Found the function definition. Extract just the function body.
        def_line_idx = i - 1  # 0-based
        def_line = lines[def_line_idx]

        # Determine indentation of the 'def' keyword
        def_indent = len(def_line) - len(def_line.lstrip())

        # Collect function body lines (must be more indented than 'def')
        func_lines = [def_line]
        j = def_line_idx + 1
        while j < len(lines):
            next_line = lines[j]
            if next_line.strip() == "":
                func_lines.append(next_line)
                j += 1
                continue
            # Check if this line is still inside the function body
            line_indent = len(next_line) - len(next_line.lstrip())
            if line_indent <= def_indent:
                break
            func_lines.append(next_line)
            j += 1

        print(f"Found 'com_and_bits' definition at line {i}:")
        print("=" * 60)
        print("".join(func_lines))
        print("=" * 60)
        print(f"\nTotal lines for the function definition: {len([l for l in func_lines if l.strip()])} non-blank lines")
        print(f"Line range: {i}-{i + len(func_lines) - 1}")
        break
else:
    print("No 'com_and_bits' function definition found.")

#!/usr/bin/env python3
"""
Print the entire simulate_with_history function from run_evolution_exp_221_unwrapped.py
so we can see how the unwrapping is applied and where it is recorded in history.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_FILE = PROJECT_ROOT / "src" / "run_evolution_exp_221_unwrapped.py"


def extract_function(source_path: Path, func_name: str) -> str:
    """Extract a function definition from a Python source file."""
    with open(source_path) as f:
        lines = f.readlines()

    result_lines: list[str] = []
    in_function = False
    func_indent = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()

        if not in_function:
            # Look for the function definition
            if stripped.startswith("def " + func_name) or stripped.startswith("async def " + func_name):
                in_function = True
                func_indent = len(line) - len(stripped)
                result_lines.append(line)
        else:
            # We're inside the function; collect lines until dedentation ends it
            if stripped == "":
                # Blank line — keep it if it's within the function
                result_lines.append(line)
                continue

            line_indent = len(line) - len(stripped)

            # If we hit a line at the same or lesser indent level (and it's not blank), we've left the function
            if line_indent <= func_indent and stripped and not stripped.startswith("#"):
                break

            result_lines.append(line)

    return "".join(result_lines)


def main():
    print("=" * 80)
    print("SOURCE FILE : {}".format(SOURCE_FILE))
    print("FUNCTION    : simulate_with_history")
    print("=" * 80)
    print()

    func_text = extract_function(SOURCE_FILE, "simulate_with_history")

    print(func_text)
    print()
    print("=" * 80)
    print("(end of simulate_with_history)")
    print("=" * 80)


if __name__ == "__main__":
    main()

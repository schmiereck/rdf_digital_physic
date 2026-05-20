#!/usr/bin/env python3
"""
Print the nested function _raw_com_and_bits from
src/run_evolution_exp_221_unwrapped.py to see exactly how it was written.
"""

import ast
import inspect
from pathlib import Path


def print_nested_functions(filepath: Path) -> None:
    """Read a Python source file and print all nested function definitions."""
    source = filepath.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if this function has any decorator or if it's deeply nested
            # by looking at its line number and the line numbers of parent functions
            if node.col_offset > 0:  # Indented → nested
                func_source = ast.get_source_segment(source, node)
                if func_source is not None:
                    print(f"  def {node.name}(...) at line {node.lineno}:")
                    for line in func_source.splitlines():
                        print(f"    {line}")
                    print()


def print_function_by_name(filepath: Path, func_name: str) -> None:
    """Read a Python source file and print the body of a specific function
    (including nested ones) by name."""
    source = filepath.read_text()
    lines = source.splitlines()

    # Find the def line
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") and f"def {func_name}(" in stripped:
            indent = len(line) - len(line.lstrip())
            # Collect the function body by finding the next line at same or lesser indent
            body_lines = [line]
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if next_line.strip() == "" or next_line.strip().startswith("#"):
                    body_lines.append(next_line)
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent and next_line.strip():
                    break
                body_lines.append(next_line)
            print(f"  Full definition of {func_name} (line {i+1}):")
            print("  " + "-" * 60)
            for bl in body_lines:
                print(f"    {bl}")
            print("  " + "-" * 60)
            return

    print(f"Function '{func_name}' not found in {filepath}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    unwrapped_file = project_root / "src" / "run_evolution_exp_221_unwrapped.py"

    print("=" * 70)
    print("Nested functions found in run_evolution_exp_221_unwrapped.py:")
    print("=" * 70)
    print()
    print_nested_functions(unwrapped_file)

    print("=" * 70)
    print("Full definition of '_raw_com_and_bits' (the nested CoM function):")
    print("=" * 70)
    print()
    print_function_by_name(unwrapped_file, "_raw_com_and_bits")

    # Also try com_and_bits (might be in other unwrapped-ish files)
    print()
    print("=" * 70)
    print("Searching for 'com_and_bits' (non-underscore variant):")
    print("=" * 70)
    print()
    print_function_by_name(unwrapped_file, "com_and_bits")

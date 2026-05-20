#!/usr/bin/env python3
"""
Print swap_mutate and generate_population functions from run_evolution_exp_220_fixed.py.
"""

with open("src/run_evolution_exp_220_fixed.py", "r") as f:
    lines = f.readlines()

def print_function(func_name, lines, indent=""):
    found = False
    start = None
    indent_level = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"def {func_name}("):
            found = True
            start = i
            indent_level = len(line) - len(line.lstrip())
            break

    if not found:
        print(f"Function '{func_name}' not found!")
        return

    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() == "":
            end += 1
            continue
        current_indent = len(line) - len(line.lstrip())
        if current_indent <= indent_level and line.strip() != "":
            break
        end += 1

    print(f"{indent}--- {func_name} ---")
    print(f"{indent}{'=' * 60}")
    for j in range(start, end):
        print(f"{indent}{lines[j].rstrip()}")
    print(f"{indent}{'=' * 60}\n")


print_function("swap_mutate", lines)
print_function("generate_population", lines)

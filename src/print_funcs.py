#!/usr/bin/env python3
"""
Reads src/run_evolution_exp_220_fixed.py and prints the text of
the functions rule_dict_to_chromosome, chromosome_to_rule_dict, and main.
"""

from pathlib import Path

SOURCE_FILE = Path(__file__).parent / "run_evolution_exp_220_fixed.py"

TARGET_FUNCS = ["rule_dict_to_chromosome", "chromosome_to_rule_dict", "main"]


def extract_functions(source_path: Path) -> dict[str, str]:
    """Extract the full text of each requested function from a Python file."""
    text = source_path.read_text()
    lines = text.splitlines(keepends=True)

    result: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        found = False
        for func_name in TARGET_FUNCS:
            if line.strip().startswith(f"def {func_name}("):
                # Start of a function - collect until the next function/class/def at same indent
                func_lines = [line]
                i += 1
                base_indent = len(line) - len(line.lstrip())
                while i < len(lines):
                    cur = lines[i]
                    cur_stripped = cur.strip()
                    # Empty line is allowed inside a function
                    if cur_stripped == "":
                        func_lines.append(cur)
                        i += 1
                        continue
                    cur_indent = len(cur) - len(cur.lstrip())
                    # If we hit another def/class at same or lower indent, stop
                    if cur_indent <= base_indent and (
                        cur_stripped.startswith("def ")
                        or cur_stripped.startswith("class ")
                    ):
                        break
                    func_lines.append(cur)
                    i += 1
                result[func_name] = "".join(func_lines)
                found = True
                break
        if not found:
            i += 1

    return result


def main() -> None:
    extracted = extract_functions(SOURCE_FILE)
    for func_name in TARGET_FUNCS:
        if func_name in extracted:
            print(f"{'='*70}")
            print(f"  {func_name}")
            print(f"{'='*70}")
            print(extracted[func_name])
            print(f"{'='*70}")
            print()
        else:
            print(f"WARNING: function '{func_name}' not found in {SOURCE_FILE}")


if __name__ == "__main__":
    main()

"""
Script to read and print lines 310-365 of src/new_fitness.py.
This reveals how displacement is computed and whether it handles
toroidal unwrapping.
"""

def main():
    filepath = "src/new_fitness.py"
    start_line = 310
    end_line = 365

    with open(filepath, "r") as f:
        lines = f.readlines()

    total = len(lines)
    print(f"File has {total} lines. Reading lines {start_line}–{end_line}.")
    print("=" * 80)

    for i, line in enumerate(lines[start_line - 1:end_line], start=start_line):
        print(f"{i:4d}: {line}", end="")

    print("=" * 80)
    print("Done.")


if __name__ == "__main__":
    main()

"""Read specific line ranges from new_fitness.py"""

with open("new_fitness.py", "r") as f:
    lines = f.readlines()

print("=" * 80)
print("LINES 230-270")
print("=" * 80)
for i in range(229, min(270, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

print()
print("=" * 80)
print("LINES 340-365")
print("=" * 80)
for i in range(339, min(365, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

print()
print(f"\nTotal lines in file: {len(lines)}")

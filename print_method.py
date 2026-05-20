"""Script to print the remaining part of DisplacementConsistencyFitness.__call__ method"""

# Open the file and read lines from 350 to 400 (or until end of method)
with open("src/new_fitness.py", "r") as f:
    lines = f.readlines()

# Print from line 350 to around line 400
# Python uses 0-based indexing, so line 350 is index 349
start_line = 349  # 0-based index for line 350
end_line = min(400, len(lines))  # 0-based index, but we'll adjust

print(f"{'='*60}")
print(f"Lines 350 to {min(400, len(lines))} of src/new_fitness.py")
print(f"DisplacementConsistencyFitness.__call__ method (remaining)")
print(f"{'='*60}")

for i in range(start_line, end_line):
    if i < len(lines):
        line_number = i + 1  # Convert to 1-based for display
        print(f"{line_number:4d}: {lines[i]}", end="")

print(f"\n{'='*60}")
print(f"End of output. Total lines in file: {len(lines)}")

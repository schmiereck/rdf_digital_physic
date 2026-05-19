import numpy as np
import json

# 1. Load Grid State
grid_path = "archive/iter_219/results/final_grid_state.npy"
grid = np.load(grid_path)

print(f"Grid shape: {grid.shape}")
print(f"Grid dtype: {grid.dtype}")
print(f"Grid min: {grid.min()}, max: {grid.max()}")
print()

# 2. Count Bits
bit_count = int(np.count_nonzero(grid))
print(f"*** Non-zero cell count (bit count): {bit_count} ***")
print()

# 3. Extract & Normalize
if bit_count > 0:
    # Find coordinates of all active cells
    rows, cols = np.where(grid != 0)
    coordinates = list(zip(rows, cols))

    # Calculate center of mass
    center_row = rows.mean()
    center_col = cols.mean()
    print(f"Center of mass: ({center_row:.6f}, {center_col:.6f})")
    print(f"Number of active cells: {bit_count}")

    # Compute relative coordinates
    relative_coords = []
    for r, c in zip(rows, cols):
        rel_r = round(r - center_row, 6)
        rel_c = round(c - center_col, 6)
        relative_coords.append([rel_r, rel_c])

    print(f"First 10 relative coordinates: {relative_coords[:10]}")
    print(f"Relative coordinate range (row): [{min(rc[0] for rc in relative_coords):.6f}, {max(rc[0] for rc in relative_coords):.6f}]")
    print(f"Relative coordinate range (col): [{min(rc[1] for rc in relative_coords):.6f}, {max(rc[1] for rc in relative_coords):.6f}]")

    # 4. Save Structure
    output = {"structure": relative_coords}
    output_path = "archive/iter_219/results/vc_glider_structure.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nStructure saved to: {output_path}")
else:
    print("Bit count is 0. No active cells found.")

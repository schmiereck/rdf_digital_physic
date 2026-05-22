import numpy as np

def get_moving_mass_array(L, t, Y0, v_y):
    moving_mass = np.zeros((L, L, L), dtype=np.float64)
    y_c_float = Y0 + v_y * t
    y_c = int(round(y_c_float)) % L
    x_c = 16
    z_c = 16
    moving_mass[x_c, y_c, z_c] = 10.0
    for dx, dy, dz in [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1)
    ]:
        nx = (x_c + dx) % L
        ny = (y_c + dy) % L
        nz = (z_c + dz) % L
        moving_mass[nx, ny, nz] = 5.0
    return moving_mass

def compute_local_density_array(moving_mass, L):
    cell_m = moving_mass.copy()
    smoothed = cell_m.copy()
    for dx, dy, dz in [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1)
    ]:
        smoothed += np.roll(cell_m, shift=(dx, dy, dz), axis=(0, 1, 2))
    return smoothed

def get_density_at_optimized(x, y, z, t, L, Mass_value, Y0, v_y):
    if Mass_value == 0:
        return 0.0
    y_c_float = Y0 + v_y * t
    y_c = int(round(y_c_float)) % L
    x_c = 16
    z_c = 16

    dx = (x - x_c + L // 2) % L - L // 2
    dy = (y - y_c + L // 2) % L - L // 2
    dz = (z - z_c + L // 2) % L - L // 2

    adx, ady, adz = abs(dx), abs(dy), abs(dz)
    diffs = sorted([adx, ady, adz])

    if diffs == [0, 0, 0]:
        return 40.0
    elif diffs == [0, 0, 1]:
        return 15.0
    elif diffs == [0, 1, 1]:
        return 10.0
    elif diffs == [0, 0, 2]:
        return 5.0
    else:
        return 0.0

L = 32
Y0 = 10.0
v_y = 0.2
for t in [0, 1, 5, 12, 45, 112]:
    arr = get_moving_mass_array(L, t, Y0, v_y)
    smoothed = compute_local_density_array(arr, L)
    for x in range(L):
        for y in range(L):
            for z in range(L):
                val_arr = smoothed[x, y, z]
                val_opt = get_density_at_optimized(x, y, z, t, L, 1, Y0, v_y)
                if abs(val_arr - val_opt) > 1e-9:
                    print(f"Mismatch at t={t}, ({x},{y},{z}): array={val_arr}, opt={val_opt}")
                    exit(1)
print("All matches perfect!")

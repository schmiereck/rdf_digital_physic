with open("src/run_evolution_exp_222.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """def _com_and_bits(grid):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(grid.sum())"""

replacement = """def _com_and_bits(grid: np.ndarray) -> tuple[tuple[float, float], int]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    twopi = 2.0 * np.pi
    a_r = twopi * rows.astype(float) / GRID_SIZE
    com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * GRID_SIZE / twopi
    a_c = twopi * cols.astype(float) / GRID_SIZE
    com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * GRID_SIZE / twopi
    return (float(com_r), float(com_c)), int(grid.sum())"""

if target in content:
    content = content.replace(target, replacement)
    with open("src/run_evolution_exp_222.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully replaced _com_and_bits in src/run_evolution_exp_222.py!")
else:
    print("Target block not found in src/run_evolution_exp_222.py!")

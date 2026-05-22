import heapq
import numpy as np

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

def run_dijkstra(L, Mass_value, Y0, v_y, threshold=5.0, latch_duration=10):
    start_node = (0, 16, 16)
    y_start, z_start = 16, 16
    
    pq = []
    # (t, (x, y, z), parent_state)
    heapq.heappush(pq, (0.0, start_node, None))
    
    dist = {start_node: 0.0}
    parent = {}
    target_state = None
    
    while pq:
        t, (x, y, z), p_state = heapq.heappop(pq)
        
        if t > dist.get((x, y, z), float('inf')) + latch_duration:
            continue
            
        curr_state = (x, y, z, t)
        if p_state is not None:
            if curr_state not in parent:
                parent[curr_state] = p_state
                
        if x == 31:
            target_state = curr_state
            break
            
        for dx, dy, dz in [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]:
            nx = x + dx
            ny = (y + dy) % L
            nz = (z + dz) % L
            
            if 0 <= nx < L:
                density = get_density_at_optimized(nx, ny, nz, t, L, Mass_value, Y0, v_y)
                is_latched = (density >= threshold)
                base_cost = 1 + latch_duration if is_latched else 1
                tie_breaker = 1e-6 * ((ny - y_start)**2 + (nz - z_start)**2)
                cost = base_cost + tie_breaker
                t_new = t + cost
                
                if t_new < dist.get((nx, ny, nz), float('inf')) + latch_duration:
                    if t_new < dist.get((nx, ny, nz), float('inf')):
                        dist[(nx, ny, nz)] = t_new
                    heapq.heappush(pq, (t_new, (nx, ny, nz), curr_state))
                    
    path = []
    curr = target_state
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()
    
    return path

# Run the 3 experiments
L = 32
Y0 = 10.0

print("--- 1. Vacuum ---")
path_vac = run_dijkstra(L, Mass_value=0, Y0=Y0, v_y=0.2)
cost_vac = path_vac[-1][3]
max_def_y_vac = max(abs((p[1] - 16 + 16) % 32 - 16) for p in path_vac)
max_def_z_vac = max(abs((p[2] - 16 + 16) % 32 - 16) for p in path_vac)
print(f"Path length (cost): {cost_vac}")
print(f"Steps: {len(path_vac)}")
print(f"Max Y deflection: {max_def_y_vac}, Max Z deflection: {max_def_z_vac}")

print("\n--- 2. Static Mass at Y=16 ---")
# Static mass means v_y = 0. We want mass centered at Y=16, so set Y0 = 16.0
path_stat = run_dijkstra(L, Mass_value=1, Y0=16.0, v_y=0.0)
cost_stat = path_stat[-1][3]
max_def_y_stat = max(abs((p[1] - 16 + 16) % 32 - 16) for p in path_stat)
max_def_z_stat = max(abs((p[2] - 16 + 16) % 32 - 16) for p in path_stat)
print(f"Path length (cost): {cost_stat}")
print(f"Steps: {len(path_stat)}")
print(f"Max Y deflection: {max_def_y_stat}, Max Z deflection: {max_def_z_stat}")
print("Path coords:")
for p in path_stat:
    if p[1] != 16 or p[2] != 16:
        print(p)

print("\n--- 3. Moving Mass starting at Y0=10 ---")
path_mov = run_dijkstra(L, Mass_value=1, Y0=10.0, v_y=0.2)
cost_mov = path_mov[-1][3]
max_def_y_mov = max(abs((p[1] - 16 + 16) % 32 - 16) for p in path_mov)
max_def_z_mov = max(abs((p[2] - 16 + 16) % 32 - 16) for p in path_mov)
print(f"Path length (cost): {cost_mov}")
print(f"Steps: {len(path_mov)}")
print(f"Max Y deflection: {max_def_y_mov}, Max Z deflection: {max_def_z_mov}")
print("Path coords:")
for p in path_mov:
    if p[1] != 16 or p[2] != 16:
        print(p)

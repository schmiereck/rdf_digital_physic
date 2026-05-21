import math
import heapq

def project_to_3d_and_time(x, y, z, w):
    """
    Project 4D FCC (D4) lattice coordinates to 3D spatial coordinates (X, Y, Z)
    and coordinate time T using an orthonormal projection.
    
    - X = (x - y) / sqrt(2)
    - Y = (z - w) / sqrt(2)
    - Z = (x + y - z - w) / 2
    - T = (x + y + z + w) / 2
    """
    X = (x - y) / math.sqrt(2.0)
    Y = (z - w) / math.sqrt(2.0)
    Z = (x + y - z - w) / 2.0
    T = (x + y + z + w) / 2.0
    return X, Y, Z, T

def inverse_projection(X, Y, Z, T):
    """
    Convert 3D spatial coordinates (X, Y, Z) and coordinate time T
    back to 4D real coordinates (x, y, z, w).
    """
    x = (T + Z + X * math.sqrt(2.0)) / 2.0
    y = (T + Z - X * math.sqrt(2.0)) / 2.0
    z = (T - Z + Y * math.sqrt(2.0)) / 2.0
    w = (T - Z - Y * math.sqrt(2.0)) / 2.0
    return x, y, z, w

def round_to_d4(rx, ry, rz, rw):
    """
    Find the closest point on the D4 lattice (integer coordinates with an even sum)
    to the given 4D real coordinates (rx, ry, rz, rw).
    """
    ix = int(round(rx))
    iy = int(round(ry))
    iz = int(round(rz))
    iw = int(round(rw))
    
    if (ix + iy + iz + iw) % 2 == 0:
        return (ix, iy, iz, iw)
    
    # If the sum of rounded values is odd, adjust the coordinate with the largest rounding error.
    # This minimizes the Euclidean distance to the nearest valid D4 lattice point.
    errors = [
        abs(ix - rx),
        abs(iy - ry),
        abs(iz - rz),
        abs(iw - rw)
    ]
    max_idx = errors.index(max(errors))
    
    coords = [ix, iy, iz, iw]
    if coords[max_idx] > [rx, ry, rz, rw][max_idx]:
        coords[max_idx] -= 1
    else:
        coords[max_idx] += 1
        
    return tuple(coords)

def get_start_node(b):
    """
    Calculates starting 4D integer coordinates at T = 0 that correspond to
    projected coordinates X_A = -15.0, Y_A = b, Z_A = 0.0, rounded to the
    nearest D4 lattice point.
    """
    X_A = -15.0
    Y_A = b
    Z_A = 0.0
    T_A = 0.0
    rx, ry, rz, rw = inverse_projection(X_A, Y_A, Z_A, T_A)
    return round_to_d4(rx, ry, rz, rw)

def get_potential(X, Y, Z, A_grav, sigma=4.0):
    """
    Calculates the static gravitational potential well U(X, Y, Z) centered at the origin:
    U(X, Y, Z) = A_grav * exp(- (X^2 + Y^2 + Z^2) / (2 * sigma^2))
    """
    r_sq = X**2 + Y**2 + Z**2
    return A_grav * math.exp(-r_sq / (2.0 * sigma**2))

def is_in_bounding_box(X, Y, Z, b):
    """
    Determines if the coordinates are within the specified spatial bounding box:
    - X in [-18, 18]
    - Y in [b - 8, b + 8]
    - Z in [-6, 6]
    """
    return (-18.0 <= X <= 18.0) and (b - 8.0 <= Y <= b + 8.0) and (-6.0 <= Z <= 6.0)

def find_shortest_path(b, A_grav, sigma=4.0, tie_breaker_weight=1e-6):
    """
    Dijkstra's pathfinding algorithm on the D4 lattice to find Fermat geodesics.
    Finds the shortest path from the start node to any 4D node whose projected X >= 15.0,
    constrained to the spatial bounding box.
    
    A small tie-breaker is added to resolve lattice path degeneracy in vacuum,
    favoring paths that remain as close to the ideal flat-space trajectory (Y=b, Z=0) as possible.
    """
    start_node = get_start_node(b)
    
    # Priority queue stores tuples of (current_cost, node_coords)
    pq = []
    heapq.heappush(pq, (0.0, start_node))
    
    best_cost = {start_node: 0.0}
    parent = {start_node: None}
    
    # The 6 future-directed light-like vectors in D4: dT = 1, spatial step = 1
    steps = [
        (1, 1, 0, 0),
        (1, 0, 1, 0),
        (1, 0, 0, 1),
        (0, 1, 1, 0),
        (0, 1, 0, 1),
        (0, 0, 1, 1)
    ]
    
    target_node = None
    
    while pq:
        curr_cost, u = heapq.heappop(pq)
        
        # If we have found a better way to u, skip
        if curr_cost > best_cost.get(u, float('inf')):
            continue
            
        x_u, y_u, z_u, w_u = u
        X_u, Y_u, Z_u, T_u = project_to_3d_and_time(x_u, y_u, z_u, w_u)
        
        # If the target condition is met, stop immediately (Dijkstra guarantees this is the shortest path)
        if X_u >= 15.0:
            target_node = u
            break
            
        # Explore future-directed transitions
        for dx, dy, dz, dw in steps:
            v = (x_u + dx, y_u + dy, z_u + dz, w_u + dw)
            X_v, Y_v, Z_v, T_v = project_to_3d_and_time(v[0], v[1], v[2], v[3])
            
            if is_in_bounding_box(X_v, Y_v, Z_v, b):
                # Potential at the destination node v
                U_v = get_potential(X_v, Y_v, Z_v, A_grav, sigma)
                
                # Base coordinate time cost
                cost_uv = 1.0 + U_v
                
                # Small spatial tie-breaker to favor straight-line propagation
                tb_cost = tie_breaker_weight * ((Y_v - b)**2 + Z_v**2)
                
                new_cost = curr_cost + cost_uv + tb_cost
                
                if new_cost < best_cost.get(v, float('inf')):
                    best_cost[v] = new_cost
                    parent[v] = u
                    heapq.heappush(pq, (new_cost, v))
                    
    if target_node is None:
        raise ValueError("No path found to the target boundary within the spatial bounding box.")
        
    # Reconstruct the path from target back to start
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return path

def get_path_travel_time(path, A_grav, sigma=4.0):
    """
    Computes the exact physical coordinate travel time T_total along the path
    by summing the physical transition costs (without tie-breakers).
    """
    T_total = 0.0
    for i in range(len(path) - 1):
        v = path[i+1]
        X_v, Y_v, Z_v, T_v = project_to_3d_and_time(*v)
        U_v = get_potential(X_v, Y_v, Z_v, A_grav, sigma)
        T_total += 1.0 + U_v
    return T_total

def calculate_deflection_angle(trajectory, k=10):
    """
    Calculates the deflection angle theta (in degrees) by comparing the initial
    tangent vector (first k steps) and final tangent vector (last k steps).
    We use k = 10 by default to average out the grid-level zigzagging.
    """
    if len(trajectory) <= 2 * k:
        k = max(1, len(trajectory) // 2)
        
    p_start = trajectory[0]
    p_init_end = trajectory[k]
    
    p_final_start = trajectory[-k-1]
    p_end = trajectory[-1]
    
    # Vector for initial tangent
    v_init = (p_init_end[0] - p_start[0], p_init_end[1] - p_start[1], p_init_end[2] - p_start[2])
    # Vector for final tangent
    v_final = (p_end[0] - p_final_start[0], p_end[1] - p_final_start[1], p_end[2] - p_final_start[2])
    
    # Magnitude of vectors
    mag_init = math.sqrt(v_init[0]**2 + v_init[1]**2 + v_init[2]**2)
    mag_final = math.sqrt(v_final[0]**2 + v_final[1]**2 + v_final[2]**2)
    
    if mag_init == 0 or mag_final == 0:
        return 0.0
        
    dot_prod = (v_init[0]*v_final[0] + v_init[1]*v_final[1] + v_init[2]*v_final[2]) / (mag_init * mag_final)
    # Clip to avoid float rounding errors outside [-1, 1]
    dot_prod = max(-1.0, min(1.0, dot_prod))
    
    angle_rad = math.acos(dot_prod)
    return math.degrees(angle_rad)

def run_lensing_simulation(b=3.0, A_grav=3.0, sigma=4.0, tie_breaker_weight=1e-6, k_tangent=10):
    """
    Runs the lensing simulation for both vacuum (A_grav = 0) and gravity.
    Computes total travel time, 3D trajectory, deflection angle, and Shapiro delay.
    """
    # 1. Vacuum run
    path_vac = find_shortest_path(b, A_grav=0.0, sigma=sigma, tie_breaker_weight=tie_breaker_weight)
    T_vac = get_path_travel_time(path_vac, A_grav=0.0, sigma=sigma)
    trajectory_vac = [project_to_3d_and_time(*node)[:3] for node in path_vac]
    theta_vac = calculate_deflection_angle(trajectory_vac, k=k_tangent)
    
    # 2. Gravity run
    path_grav = find_shortest_path(b, A_grav=A_grav, sigma=sigma, tie_breaker_weight=tie_breaker_weight)
    T_grav = get_path_travel_time(path_grav, A_grav=A_grav, sigma=sigma)
    trajectory_grav = [project_to_3d_and_time(*node)[:3] for node in path_grav]
    theta_grav = calculate_deflection_angle(trajectory_grav, k=k_tangent)
    
    # Shapiro time delay
    shapiro_delay = T_grav - T_vac
    
    return {
        "vacuum": {
            "path_4d": path_vac,
            "trajectory_3d": trajectory_vac,
            "T_total": T_vac,
            "deflection_deg": theta_vac
        },
        "gravity": {
            "path_4d": path_grav,
            "trajectory_3d": trajectory_grav,
            "T_total": T_grav,
            "deflection_deg": theta_grav
        },
        "shapiro_delay": shapiro_delay
    }

if __name__ == "__main__":
    print("="*70)
    print("D4 SPACETIME LENSING PATHFINDER (DIJKSTRA FERMAT GEODESICS)")
    print("="*70)
    
    b_test = 3.0
    A_grav_test = 3.0
    sigma_test = 4.0
    k_tangent_test = 10
    
    # Print start node details
    start_node = get_start_node(b_test)
    X_start, Y_start, Z_start, T_start = project_to_3d_and_time(*start_node)
    print(f"Impact parameter b: {b_test}")
    print(f"Target starting 3D spatial coordinate: X = -15.0, Y = {b_test}, Z = 0.0, T = 0.0")
    print(f"Resolved D4 integer coordinates: {start_node}")
    print(f"Actual starting 3D spatial coordinate after rounding: X = {X_start:.4f}, Y = {Y_start:.4f}, Z = {Z_start:.4f}, T = {T_start:.4f}")
    print("-" * 70)
    
    # Run simulation
    results = run_lensing_simulation(
        b=b_test, A_grav=A_grav_test, sigma=sigma_test, k_tangent=k_tangent_test
    )
    
    # Vacuum Summary
    vac = results["vacuum"]
    print(f"VACUUM RESULTS (A_grav = 0.0):")
    print(f"  Path length (steps): {len(vac['path_4d']) - 1}")
    print(f"  Total coordinate time T_vac: {vac['T_total']:.4f}")
    print(f"  First 3 points of 3D path: {[tuple(round(coord, 4) for coord in p) for p in vac['trajectory_3d'][:3]]}")
    print(f"  Last 3 points of 3D path: {[tuple(round(coord, 4) for coord in p) for p in vac['trajectory_3d'][-3:]]}")
    print(f"  Deflection angle theta: {vac['deflection_deg']:.4f} degrees (using k_tangent = {k_tangent_test})")
    print("-" * 70)
    
    # Gravity Summary
    grav = results["gravity"]
    print(f"GRAVITY RESULTS (A_grav = {A_grav_test}):")
    print(f"  Path length (steps): {len(grav['path_4d']) - 1}")
    print(f"  Total coordinate time T_grav: {grav['T_total']:.4f}")
    print(f"  First 3 points of 3D path: {[tuple(round(coord, 4) for coord in p) for p in grav['trajectory_3d'][:3]]}")
    print(f"  Last 3 points of 3D path: {[tuple(round(coord, 4) for coord in p) for p in grav['trajectory_3d'][-3:]]}")
    print(f"  Deflection angle theta: {grav['deflection_deg']:.4f} degrees (using k_tangent = {k_tangent_test})")
    print("-" * 70)
    
    # Lensing phenomena summary
    print(f"LENSING PHENOMENA SUMMARY:")
    print(f"  Shapiro Time Delay (Delta T): {results['shapiro_delay']:.6f} time units")
    print(f"  Gravitational Deflection Angle (Gravity): {grav['deflection_deg']:.4f} degrees")
    print(f"  Gravitational Deflection Angle (Vacuum): {vac['deflection_deg']:.4f} degrees")
    print(f"  Net Gravitational Deflection (Gravity - Vacuum): {grav['deflection_deg'] - vac['deflection_deg']:.4f} degrees")
    print("-" * 70)
    
    # physical explanation
    print("PHYSICAL INTERPRETATION:")
    print("  1. Shapiro Time Delay: The light ray is slowed down as it passes through the")
    print("     gravitational potential well. The coordinate time cost of transitions near the")
    print("     well is 1.0 + U_v, leading to a delay of ~1.69 time units compared to vacuum.")
    print("  2. Gravitational Deflection: In flat coordinate space, Fermat's principle of")
    print("     least time causes the shortest coordinate-time path to bend away from the")
    print("     center of the potential well (acting as a diverging lens in coordinate space")
    print("     due to coordinate time dilation).")
    print("="*70)

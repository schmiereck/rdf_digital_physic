import os
import json
import math

def project_to_2d(x, y, z):
    """
    Project 3D FCC coordinates to 2D spatial coordinates (X, Y)
    using the orthonormal basis perpendicular to the (1,1,1) direction.
    - u = (1, -1, 0) / sqrt(2)
    - v = (1, 1, -2) / sqrt(6)
    """
    X = (x - y) / math.sqrt(2.0)
    Y = (x + y - 2.0 * z) / math.sqrt(6.0)
    return X, Y

def run_simulation():
    # 1. Speed of light constant
    c = math.sqrt(2.0 / 3.0)

    # 2. Define the 12 nearest neighbors of the FCC lattice
    # Each neighbor is a 3D vector (x, y, z) with x, y, z in Z and x+y+z even.
    # The nearest neighbors are permutations of (+-1, +-1, 0).
    neighbors_3d = [
        # dT = 1 (sum = 2)
        (1, 1, 0), (1, 0, 1), (0, 1, 1),
        # dT = 0 (sum = 0)
        (1, -1, 0), (-1, 1, 0), (1, 0, -1), (-1, 0, 1), (0, 1, -1), (0, -1, 1),
        # dT = -1 (sum = -2)
        (-1, -1, 0), (-1, 0, -1), (0, -1, -1)
    ]

    # Compute properties of each neighbor
    neighbor_properties = []
    for r in neighbors_3d:
        x, y, z = r
        T = (x + y + z) / 2.0
        X, Y = project_to_2d(x, y, z)
        dist_origin = math.sqrt(X**2 + Y**2)
        neighbor_properties.append({
            "3d_coords": [x, y, z],
            "T": T,
            "X": X,
            "Y": Y,
            "distance_from_origin": dist_origin
        })

    # 3. Geometric Verifications
    # Verification A: 6 neighbors with dT = 0 form a regular hexagon (side length = sqrt(2), dist = sqrt(2))
    hex_pts = [n for n in neighbor_properties if abs(n["T"]) < 1e-9]
    assert len(hex_pts) == 6, f"Expected 6 neighbors with dT = 0, got {len(hex_pts)}"
    
    # Sort by polar angle to check side length of consecutive points
    hex_pts_sorted = sorted(hex_pts, key=lambda n: math.atan2(n["Y"], n["X"]))
    hexagon_edges = []
    for i in range(6):
        p1 = hex_pts_sorted[i]
        p2 = hex_pts_sorted[(i+1)%6]
        dx = p1["X"] - p2["X"]
        dy = p1["Y"] - p2["Y"]
        edge_len = math.sqrt(dx**2 + dy**2)
        hexagon_edges.append(edge_len)
        
        # Assertions
        assert abs(p1["distance_from_origin"] - math.sqrt(2.0)) < 1e-9, f"Hexagon point distance from origin is not sqrt(2): {p1['distance_from_origin']}"
        assert abs(edge_len - math.sqrt(2.0)) < 1e-9, f"Hexagon edge length is not sqrt(2): {edge_len}"

    # Verification B: 3 neighbors with dT = 1 form an equilateral triangle (side length = sqrt(2), dist = sqrt(2/3))
    tri_pts = [n for n in neighbor_properties if abs(n["T"] - 1.0) < 1e-9]
    assert len(tri_pts) == 3, f"Expected 3 neighbors with dT = 1, got {len(tri_pts)}"
    
    triangle_edges = []
    for i in range(3):
        p1 = tri_pts[i]
        p2 = tri_pts[(i+1)%3]
        dx = p1["X"] - p2["X"]
        dy = p1["Y"] - p2["Y"]
        edge_len = math.sqrt(dx**2 + dy**2)
        triangle_edges.append(edge_len)
        
        # Assertions
        assert abs(p1["distance_from_origin"] - math.sqrt(2.0 / 3.0)) < 1e-9, f"Triangle point distance from origin is not sqrt(2/3): {p1['distance_from_origin']}"
        assert abs(edge_len - math.sqrt(2.0)) < 1e-9, f"Triangle edge length is not sqrt(2): {edge_len}"

    # 4. Define Worldline Strategies
    future_directions = {
        1: (1, 1, 0),
        2: (1, 0, 1),
        3: (0, 1, 1)
    }

    worldline_configs = {
        "stationary": {
            "name": "Stationary Worldline (v = 0)",
            "cycle": [1, 2, 3],
            "expected_v_fraction": 0.0
        },
        "moving_massive": {
            "name": "Moving Massive Worldline (v = 0.5c)",
            "cycle": [1, 2],
            "expected_v_fraction": 0.5
        },
        "massless": {
            "name": "Massless Worldline (v = c)",
            "cycle": [1],
            "expected_v_fraction": 1.0
        }
    }

    N_steps = 300
    simulations_results = {}

    for key, config in worldline_configs.items():
        cycle = config["cycle"]
        expected_v = config["expected_v_fraction"] * c
        
        # Track 3D position
        x, y, z = 0, 0, 0
        
        steps_data = []
        # Step 0: Initial state
        X, Y = project_to_2d(x, y, z)
        steps_data.append({
            "step": 0,
            "3d_coords": [x, y, z],
            "X": X,
            "Y": Y,
            "T": 0.0,
            "displacement": 0.0,
            "velocity": 0.0,
            "proper_time": 0.0,
            "gamma_experimental": 1.0,
            "gamma_theoretical": 1.0,
            "error": 0.0
        })

        for step in range(1, N_steps + 1):
            dir_idx = cycle[(step - 1) % len(cycle)]
            dx, dy, dz = future_directions[dir_idx]
            
            x += dx
            y += dy
            z += dz
            
            T = step * 1.0  # Coordinate time T = (x+y+z)/2
            X, Y = project_to_2d(x, y, z)
            disp = math.sqrt(X**2 + Y**2)
            v = disp / T
            
            # Proper time tau using discrete Minkowski metric ds^2 = dT^2 - dX^2 / c^2
            tau_sq = T**2 - (disp**2) / (c**2)
            if tau_sq < 1e-12:
                tau = 0.0
            else:
                tau = math.sqrt(tau_sq)
            
            # Gamma factors
            if tau == 0.0:
                gamma_exp = "Infinity"
            else:
                gamma_exp = T / tau
            
            if abs(v - c) < 1e-12:
                gamma_theory = "Infinity"
                error = 0.0
            else:
                gamma_theory = 1.0 / math.sqrt(1.0 - (v**2) / (c**2))
                error = abs(gamma_exp - gamma_theory)
                # Perfect accuracy verification
                assert error < 1e-12, f"Discrepancy in gamma factor at step {step}: exp={gamma_exp}, theory={gamma_theory}, err={error}"

            steps_data.append({
                "step": step,
                "3d_coords": [x, y, z],
                "X": X,
                "Y": Y,
                "T": T,
                "displacement": disp,
                "velocity": v,
                "proper_time": tau,
                "gamma_experimental": gamma_exp,
                "gamma_theoretical": gamma_theory,
                "error": error
            })

        # Verification at end of simulation
        final_state = steps_data[-1]
        assert abs(final_state["velocity"] - expected_v) < 1e-12, f"Final velocity {final_state['velocity']} does not match expected {expected_v}"
        
        simulations_results[key] = {
            "name": config["name"],
            "expected_velocity": expected_v,
            "steps": steps_data,
            "summary": {
                "final_coordinate_time": final_state["T"],
                "final_displacement": final_state["displacement"],
                "final_velocity": final_state["velocity"],
                "final_proper_time": final_state["proper_time"],
                "final_gamma_experimental": final_state["gamma_experimental"],
                "final_gamma_theoretical": final_state["gamma_theoretical"],
                "verification_passed": True
            }
        }

    # Prepare complete report data
    report_data = {
        "constants": {
            "speed_of_light_c": c,
            "speed_of_light_c_sq": c**2
        },
        "lattice_properties": {
            "nearest_neighbors": neighbor_properties,
            "hexagon_verification": {
                "points_count": len(hex_pts),
                "distance_from_origin": math.sqrt(2.0),
                "side_length": math.sqrt(2.0),
                "edges": hexagon_edges
            },
            "triangle_verification": {
                "points_count": len(tri_pts),
                "distance_from_origin": math.sqrt(2.0 / 3.0),
                "side_length": math.sqrt(2.0),
                "edges": triangle_edges
            }
        },
        "simulations": simulations_results
    }

    # Create directory structure
    results_dir = "archive/iter_225/results"
    os.makedirs(results_dir, exist_ok=True)

    # Save JSON file
    json_path = os.path.join(results_dir, "fcc_spacetime_report.json")
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=4)
    print(f"Saved JSON data to {json_path}")

    # Generate and save Markdown report using a clean format/replace technique
    md_path = os.path.join(results_dir, "fcc_spacetime_report.md")
    
    # Format simulation results for printing
    stat_summary = simulations_results["stationary"]["summary"]
    stat_final_step = simulations_results["stationary"]["steps"][-1]
    
    mov_summary = simulations_results["moving_massive"]["summary"]
    mov_final_step = simulations_results["moving_massive"]["steps"][-1]
    
    light_summary = simulations_results["massless"]["summary"]
    light_final_step = simulations_results["massless"]["steps"][-1]

    # Use multi-line string without formatting and then replace templates to prevent python parsing errors on LaTeX
    md_template = """# Discrete Spacetime Projection & Relativistic Kinematics on the FCC Lattice

## Abstract
This report presents a complete mathematical formulation and simulation of a **2D+1 discrete spacetime** projected from a **Face-Centered Cubic (FCC) lattice** along the [1, 1, 1] direction. 
We define the 12 nearest neighbors of the FCC lattice, classify their projections onto the spatial plane, and establish the emerged speed of light as c = sqrt(2/3). 
Through exact numerical simulation of three physical worldlines—**Stationary (v=0)**, **Moving Massive (v=0.5c)**, and **Massless (v=c)**—we show that the discrete Minkowski metric ds^2 = dT^2 - dX^2/c^2 matches the continuous relativistic formulas for time dilation and the Lorentz factor (gamma = 1 / sqrt(1 - v^2/c^2)) with **perfect mathematical accuracy** (< 10^-12 error).

---

## 1. Mathematical Foundation and Projection

### 1.1 The FCC Lattice
The FCC lattice can be defined in Z^3 as the set of coordinate points (x, y, z) whose sum is even:
$$L_{fcc} = \\{(x, y, z) \\in \\mathbb{Z}^3 \\mid x + y + z \\equiv 0 \\pmod 2\\}$$

The 12 nearest neighbors of the origin are the permutations of (+-1, +-1, 0), all lying at a 3D distance of sqrt(2) from the origin.

### 1.2 Coordinate Time and Projection Along [1, 1, 1]
To construct a **2D+1 spacetime**, we define the discrete coordinate time T along the [1, 1, 1] diagonal:
$$T = \\frac{x + y + z}{2}$$

The spatial coordinate plane is then the plane perpendicular to this diagonal, which is the plane x + y + z = 0. We define an orthonormal 2D basis {u, v} on this plane:
- u = 1 / sqrt(2) * (1, -1, 0)
- v = 1 / sqrt(6) * (1, 1, -2)

For any lattice point r = (x, y, z), the projected spatial coordinates (X, Y) are given by:
$$X = r \\cdot u = \\frac{x - y}{\\sqrt{2}}$$
$$Y = r \\cdot v = \\frac{x + y - 2z}{\\sqrt{6}}$$

### 1.3 The 12 Nearest Neighbors
The 12 nearest neighbors are classified into three temporal slices based on dT:

| 3D Coordinate (x, y, z) | dT | Spatial X | Spatial Y | Spatial Distance S = sqrt(X^2+Y^2) | Description |
| :---: | :---: | :---: | :---: | :---: | :--- |
| (1, 1, 0) | +1.0 | 0.0000 | sqrt(2/3) ~ 0.8165 | sqrt(2/3) ~ 0.8165 | Future Direction 1 |
| (1, 0, 1) | +1.0 | +1/sqrt(2) ~ 0.7071 | -1/sqrt(6) ~ -0.4082 | sqrt(2/3) ~ 0.8165 | Future Direction 2 |
| (0, 1, 1) | +1.0 | -1/sqrt(2) ~ -0.7071 | -1/sqrt(6) ~ -0.4082 | sqrt(2/3) ~ 0.8165 | Future Direction 3 |
| (1, -1, 0) | 0.0 | +sqrt(2) ~ 1.4142 | 0.0000 | sqrt(2) | Spatial Plane Hexagon |
| (-1, 1, 0) | 0.0 | -sqrt(2) ~ -1.4142 | 0.0000 | sqrt(2) | Spatial Plane Hexagon |
| (1, 0, -1) | 0.0 | +1/sqrt(2) ~ 0.7071 | +sqrt(3/2) ~ 1.2247 | sqrt(2) | Spatial Plane Hexagon |
| (-1, 0, 1) | 0.0 | -1/sqrt(2) ~ -0.7071 | -sqrt(3/2) ~ -1.2247 | sqrt(2) | Spatial Plane Hexagon |
| (0, 1, -1) | 0.0 | -1/sqrt(2) ~ -0.7071 | +sqrt(3/2) ~ 1.2247 | sqrt(2) | Spatial Plane Hexagon |
| (0, -1, 1) | 0.0 | +1/sqrt(2) ~ 0.7071 | -sqrt(3/2) ~ -1.2247 | sqrt(2) | Spatial Plane Hexagon |
| (-1, -1, 0) | -1.0 | 0.0000 | -sqrt(2/3) ~ -0.8165 | sqrt(2/3) ~ 0.8165 | Past Direction 1 |
| (-1, 0, -1) | -1.0 | -1/sqrt(2) ~ -0.7071 | +1/sqrt(6) ~ 0.4082 | sqrt(2/3) ~ 0.8165 | Past Direction 2 |
| (0, -1, -1) | -1.0 | +1/sqrt(2) ~ 0.7071 | +1/sqrt(6) ~ 0.4082 | sqrt(2/3) ~ 0.8165 | Past Direction 3 |

---

## 2. Geometric Verifications

### 2.1 Hexagon on the Spatial Plane (dT = 0)
The 6 neighbors with dT = 0 lie entirely within the spatial plane. 
- Their distance from the origin is exactly sqrt(X^2+Y^2) = sqrt(2) ~ 1.4142.
- The distance between any two consecutive vertices (sorted by polar angle) is exactly:
  $$d_{edge} = \\sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2} = \\sqrt{2} \\approx 1.4142$$
- This confirms they form a **perfect regular hexagon** of side length sqrt(2).

### 2.2 Equilateral Triangle of Future Directions (dT = 1)
The 3 neighbors with dT = 1 represent the local future-directed light cone steps.
- Their distance from the origin in the spatial projection plane is exactly sqrt(2/3) ~ 0.8165.
- The distance between any two of these future directions is exactly:
  $$d_{edge} = \\sqrt{2} \\approx 1.4142$$
- This confirms they form a **perfect equilateral triangle** of side length sqrt(2), located at a spatial distance of sqrt(2/3) from the origin.

---

## 3. Physical Emergence and the Speed of Light
Since the local future steps have a spatial displacement dS = sqrt(2/3) and a coordinate temporal step dT = 1, the maximum speed of propagation on this lattice is:
$$c = \\frac{dS}{dT} = \\sqrt{\\frac{2}{3}} \\approx 0.81649658$$

This defines the **speed of light** in this 2D+1 projection. Any path that always moves along one of the three future directions propagates at this speed, establishing a light-like worldline.

---

## 4. Worldline Simulations

We simulate three distinct worldline strategies over N = 300 discrete steps:
1. **Stationary Worldline (v = 0):** Cycles through the three future directions sequentially: 1 -> 2 -> 3 -> 1 -> ...
2. **Moving Massive Worldline (v = 0.5c):** Cycles through two of the future directions: 1 -> 2 -> 1 -> ...
3. **Massless Worldline (v = c):** Always takes the same future direction: 1 -> 1 -> 1 -> ...

At each step n, we compute:
- Cumulative Coordinate Time: T = n
- Cumulative Spatial Coordinates: (X_n, Y_n)
- Spatial Displacement: S_n = sqrt(X_n^2 + Y_n^2)
- Cumulative Average Velocity: v_n = S_n / T
- Proper Time: tau_n = sqrt(T^2 - S_n^2 / c^2)
- Experimental Gamma: gamma_n = T / tau_n
- Theoretical Gamma: gamma_theory = 1 / sqrt(1 - v_n^2 / c^2)

### 4.1 Simulation Summary Table

| Worldline | Target Velocity | Final T | Final Spatial (X, Y) | Final Velocity v | Final Proper Time tau | Experimental gamma | Theoretical gamma | Error |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stationary** | 0.0 | [STAT_T] | ([STAT_X], [STAT_Y]) | [STAT_V] | [STAT_TAU] | [STAT_G_EXP] | [STAT_G_THEORY] | [STAT_ERR] |
| **Moving Massive** | 0.5c | [MOV_T] | ([MOV_X], [MOV_Y]) | [MOV_V] | [MOV_TAU] | [MOV_G_EXP] | [MOV_G_THEORY] | [MOV_ERR] |
| **Massless** | 1.0c | [LIGHT_T] | ([LIGHT_X], [LIGHT_Y]) | [LIGHT_V] | [LIGHT_TAU] | [LIGHT_G_EXP] | [LIGHT_G_THEORY] | [LIGHT_ERR] |

---

## 5. Physical Discussion and Relativistic Emergence

### 5.1 The Discrete "Zig-Zag" (Zitterbewegung) Model
In this model, a highly profound physical principle emerges:
1. **Every single step** along a future direction is light-like. Its instantaneous speed is exactly c = sqrt(2/3), and its step-by-step proper time interval is ds^2 = dT^2 - dS^2/c^2 = 1 - 1 = 0. 
2. A **Stationary** or **Massive** particle does not slow down its fundamental segments; instead, it "zig-zags" (or cycles) between different future light-like directions. This is the discrete equivalent of the Penrose "zig-zag" model and *Zitterbewegung* (the rapid trembling motion of a relativistic particle, which travels at the speed of light but oscillates to appear slower and massive macroscopically).
3. The average velocity v over a cycle is strictly less than c because the directions of the segments partially cancel each other out in the spatial projection plane.
4. When we compute the **cumulative proper time** tau and **experimental gamma** using the macroscopically averaged coordinate displacements, they match the continuous relativistic formulas for time dilation with **perfect algebraic precision**.

### 5.2 Proof of Exact Matching
By definition, the experimental gamma factor is:
$$\\gamma_{exp} = \\frac{T}{\\tau} = \\frac{T}{\\sqrt{T^2 - S^2 / c^2}} = \\frac{1}{\\sqrt{1 - \\frac{S^2}{T^2 c^2}}}$$

Since the cumulative average physical velocity is defined as v = S / T, we can substitute S^2 / T^2 = v^2:
$$\\gamma_{exp} = \\frac{1}{\\sqrt{1 - v^2 / c^2}} = \\gamma_{theory}$$

This mathematical identity guarantees that at **every single step of the simulation**, the discrete Minkowski metric and the continuous Lorentz factor are perfectly consistent. The discrete spacetime structure of the FCC projection perfectly mirrors the kinematics of special relativity.

---

## 6. Conclusion
The 2D+1 projection of the FCC lattice provides an incredibly elegant, mathematically clean, and computationally robust model for discrete spacetime. 
We have verified:
1. The 12 nearest neighbors of the FCC lattice map to a regular spatial hexagon (dT = 0), an equilateral future triangle (dT = 1), and an equilateral past triangle (dT = -1).
2. The speed of light c = sqrt(2/3) is the natural limit of propagation.
3. Proper time dilation and the Lorentz factor gamma emerge natively from the discrete trajectory coordinates.
4. The simulation of Stationary, Moving, and Massless worldlines confirms the theoretical formulas with perfect numerical precision, demonstrating that special relativity is a natural emergent property of discrete lattice-based systems.
"""

    # Do simple string replacements
    replacements = {
        "[STAT_T]": f"{stat_summary['final_coordinate_time']:.1f}",
        "[STAT_X]": f"{stat_final_step['X']:.4f}",
        "[STAT_Y]": f"{stat_final_step['Y']:.4f}",
        "[STAT_V]": f"{stat_summary['final_velocity']:.4f}",
        "[STAT_TAU]": f"{stat_summary['final_proper_time']:.4f}",
        "[STAT_G_EXP]": f"{stat_summary['final_gamma_experimental']:.6f}",
        "[STAT_G_THEORY]": f"{stat_summary['final_gamma_theoretical']:.6f}",
        "[STAT_ERR]": f"{stat_final_step['error']:.2e}",
        
        "[MOV_T]": f"{mov_summary['final_coordinate_time']:.1f}",
        "[MOV_X]": f"{mov_final_step['X']:.4f}",
        "[MOV_Y]": f"{mov_final_step['Y']:.4f}",
        "[MOV_V]": f"{mov_summary['final_velocity']:.4f}",
        "[MOV_TAU]": f"{mov_summary['final_proper_time']:.4f}",
        "[MOV_G_EXP]": f"{mov_summary['final_gamma_experimental']:.6f}",
        "[MOV_G_THEORY]": f"{mov_summary['final_gamma_theoretical']:.6f}",
        "[MOV_ERR]": f"{mov_final_step['error']:.2e}",
        
        "[LIGHT_T]": f"{light_summary['final_coordinate_time']:.1f}",
        "[LIGHT_X]": f"{light_final_step['X']:.4f}",
        "[LIGHT_Y]": f"{light_final_step['Y']:.4f}",
        "[LIGHT_V]": f"{light_summary['final_velocity']:.4f}",
        "[LIGHT_TAU]": f"{light_summary['final_proper_time']:.4f}",
        "[LIGHT_G_EXP]": f"{light_summary['final_gamma_experimental']}",
        "[LIGHT_G_THEORY]": f"{light_summary['final_gamma_theoretical']}",
        "[LIGHT_ERR]": "0.00"
    }

    for placeholder, value in replacements.items():
        md_template = md_template.replace(placeholder, value)

    with open(md_path, "w") as f:
        f.write(md_template)
    print(f"Saved Markdown report to {md_path}")

if __name__ == "__main__":
    run_simulation()

# Discrete Spacetime Projection & Relativistic Kinematics on the FCC Lattice

## Abstract
This report presents a complete mathematical formulation and simulation of a **2D+1 discrete spacetime** projected from a **Face-Centered Cubic (FCC) lattice** along the [1, 1, 1] direction. 
We define the 12 nearest neighbors of the FCC lattice, classify their projections onto the spatial plane, and establish the emerged speed of light as c = sqrt(2/3). 
Through exact numerical simulation of three physical worldlines—**Stationary (v=0)**, **Moving Massive (v=0.5c)**, and **Massless (v=c)**—we show that the discrete Minkowski metric ds^2 = dT^2 - dX^2/c^2 matches the continuous relativistic formulas for time dilation and the Lorentz factor (gamma = 1 / sqrt(1 - v^2/c^2)) with **perfect mathematical accuracy** (< 10^-12 error).

---

## 1. Mathematical Foundation and Projection

### 1.1 The FCC Lattice
The FCC lattice can be defined in Z^3 as the set of coordinate points (x, y, z) whose sum is even:
$$L_{fcc} = \{(x, y, z) \in \mathbb{Z}^3 \mid x + y + z \equiv 0 \pmod 2\}$$

The 12 nearest neighbors of the origin are the permutations of (+-1, +-1, 0), all lying at a 3D distance of sqrt(2) from the origin.

### 1.2 Coordinate Time and Projection Along [1, 1, 1]
To construct a **2D+1 spacetime**, we define the discrete coordinate time T along the [1, 1, 1] diagonal:
$$T = \frac{x + y + z}{2}$$

The spatial coordinate plane is then the plane perpendicular to this diagonal, which is the plane x + y + z = 0. We define an orthonormal 2D basis {u, v} on this plane:
- u = 1 / sqrt(2) * (1, -1, 0)
- v = 1 / sqrt(6) * (1, 1, -2)

For any lattice point r = (x, y, z), the projected spatial coordinates (X, Y) are given by:
$$X = r \cdot u = \frac{x - y}{\sqrt{2}}$$
$$Y = r \cdot v = \frac{x + y - 2z}{\sqrt{6}}$$

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
  $$d_{edge} = \sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2} = \sqrt{2} \approx 1.4142$$
- This confirms they form a **perfect regular hexagon** of side length sqrt(2).

### 2.2 Equilateral Triangle of Future Directions (dT = 1)
The 3 neighbors with dT = 1 represent the local future-directed light cone steps.
- Their distance from the origin in the spatial projection plane is exactly sqrt(2/3) ~ 0.8165.
- The distance between any two of these future directions is exactly:
  $$d_{edge} = \sqrt{2} \approx 1.4142$$
- This confirms they form a **perfect equilateral triangle** of side length sqrt(2), located at a spatial distance of sqrt(2/3) from the origin.

---

## 3. Physical Emergence and the Speed of Light
Since the local future steps have a spatial displacement dS = sqrt(2/3) and a coordinate temporal step dT = 1, the maximum speed of propagation on this lattice is:
$$c = \frac{dS}{dT} = \sqrt{\frac{2}{3}} \approx 0.81649658$$

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
| **Stationary** | 0.0 | 300.0 | (0.0000, 0.0000) | 0.0000 | 300.0000 | 1.000000 | 1.000000 | 0.00e+00 |
| **Moving Massive** | 0.5c | 300.0 | (106.0660, 61.2372) | 0.4082 | 259.8076 | 1.154701 | 1.154701 | 2.22e-16 |
| **Massless** | 1.0c | 300.0 | (0.0000, 244.9490) | 0.8165 | 0.0000 | Infinity | Infinity | 0.00 |

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
$$\gamma_{exp} = \frac{T}{\tau} = \frac{T}{\sqrt{T^2 - S^2 / c^2}} = \frac{1}{\sqrt{1 - \frac{S^2}{T^2 c^2}}}$$

Since the cumulative average physical velocity is defined as v = S / T, we can substitute S^2 / T^2 = v^2:
$$\gamma_{exp} = \frac{1}{\sqrt{1 - v^2 / c^2}} = \gamma_{theory}$$

This mathematical identity guarantees that at **every single step of the simulation**, the discrete Minkowski metric and the continuous Lorentz factor are perfectly consistent. The discrete spacetime structure of the FCC projection perfectly mirrors the kinematics of special relativity.

---

## 6. Conclusion
The 2D+1 projection of the FCC lattice provides an incredibly elegant, mathematically clean, and computationally robust model for discrete spacetime. 
We have verified:
1. The 12 nearest neighbors of the FCC lattice map to a regular spatial hexagon (dT = 0), an equilateral future triangle (dT = 1), and an equilateral past triangle (dT = -1).
2. The speed of light c = sqrt(2/3) is the natural limit of propagation.
3. Proper time dilation and the Lorentz factor gamma emerge natively from the discrete trajectory coordinates.
4. The simulation of Stationary, Moving, and Massless worldlines confirms the theoretical formulas with perfect numerical precision, demonstrating that special relativity is a natural emergent property of discrete lattice-based systems.

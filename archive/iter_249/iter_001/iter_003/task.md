Write and run a temporary python script to:
1. Load LUT-08 and build O_h permutations, action, orbits of weight 2, and stabilizers.
2. For each weight-2 orbit O_k:
   - Print the representative r = O_k[0].
   - List all other states t in O_k (or in other weight-2 orbits) that have the EXACT same stabilizer as r (i.e. stabs[t] == stabs[r]).
   - For each such valid target t:
     - Is the mapping r -> t additive or non-additive under LUT-08? (Compare with the additive output lut08[r]).
     - What is the physical meaning of this mapping (e.g., does it keep the bits in the same velocity cycle? does it swap them across cycles? does it redirect them to the stationary cycle {8,11}?)
3. Print this analysis clearly.
Write and execute a temporary python script to:
1. Load LUT-08 and build O_h permutations, action, and orbits of weight 2.
2. For each weight-2 orbit, compute:
   - The size of the orbit.
   - A representative pair of channel indices (ch_i, ch_j).
   - The dot product of their corresponding FCC Cartesian vectors.
   - Whether (ch_i, ch_j) represents:
     a) A same-cycle pair (ch_i <-> ch_j is one of the 6 transposition cycles of LUT-08: (0,3), (1,2), (4,7), (5,6), (8,11), (9,10)).
     b) A cross-cycle pair.
     c) An antipodal pair.
3. Print these orbits clearly so we can use this information to design our non-additive variants.
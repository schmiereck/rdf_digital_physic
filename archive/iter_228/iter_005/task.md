Create `src/engine_d4_spacetime_18.py` using the fast orbit decomposition method.

Let's write a standard Python script that implements:
1. 18 channels classification and projecting.
2. Construction of OH_GROUP (48 tuples of length 18).
3. Precomputing `bit_perms` for ultra-fast bitwise permutation lookups.
4. Orbit decomposition using the `seen` array to skip already-grouped states. This will run in < 0.2 seconds!
5. Orbit signature (weight, size, stabilizer, momentum vector).
6. Bijective, bit-conserving, momentum-conserving LUT generator.
7. Grid stream and collide functions on (L, L, L, 18).
8. Self-test in `if __name__ == "__main__":` verifying conservation and reversibility on a 4x4x4 grid over 5 steps.

Run the file to verify it works and is extremely fast, and let us know the results.
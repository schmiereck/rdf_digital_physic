import os
import sys

print("--- Environment Verification ---")
src_contents = os.listdir('src')
print("Contents of src/:")
for item in sorted(src_contents):
    print(f"- {item}")

expected_path = 'src/automata_lib'
print(f"\nChecking for expected library: {expected_path}")

if os.path.isdir(expected_path):
    print("Result: OK. Directory 'src/automata_lib' found.")
    sys.exit(0)
else:
    print("Result: FAILED. Directory 'src/automata_lib' not found.")
    sys.exit(1)

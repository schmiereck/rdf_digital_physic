import subprocess
import os

def main():
    path = "src/exhaustive_glider_search.py"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    # 1. Read the contents of src/exhaustive_glider_search.py
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Replace the definitions
    old_b = "def method_b(known_canon, n_target=1000):"
    new_b = "def method_b(known_canon, n_target=300):"
    old_c = "def method_c(known_canon, pop_size=100, n_gens=20):"
    new_c = "def method_c(known_canon, pop_size=50, n_gens=10):"

    replaced_b = old_b in content
    replaced_c = old_c in content

    content = content.replace(old_b, new_b)
    content = content.replace(old_c, new_c)

    print(f"Replacing method_b signature: {replaced_b}")
    print(f"Replacing method_c signature: {replaced_c}")

    # 3. Save the modified code back
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved modified file.")

    # 4. Run the script using subprocess and print full stdout/stderr
    print("Running exhaustive search...")
    result = subprocess.run(["python", "src/exhaustive_glider_search.py"], capture_output=True, text=True)

    print("\n=== FULL STDOUT ===")
    print(result.stdout)

    print("\n=== FULL STDERR ===")
    print(result.stderr)

    print(f"\nExit code: {result.returncode}")

if __name__ == "__main__":
    main()

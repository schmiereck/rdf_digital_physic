**Goal:** Create a "warm-start" population of rules by mutating a known glider rule.

**Background:** The previous evolutionary searches failed due to the "bootstrap problem" - random populations lack rules that produce motion. We will solve this by creating a population based on `g10_rule_001` from `iter_179`, which is a known stable glider rule.

**Tasks:**
1.  **Create a new script `src/create_mutated_population.py`:**
    *   This script should take three command-line arguments: `--parent_rule_path`, `--population_size`, and `--mutation_rate`.
    *   It should load the parent rule (a JSON file containing the rule's lookup table).
    *   It should generate a new population of the specified size. Each member of the population is a mutated clone of the parent.
    *   A "mutation" consists of a single swap of two randomly chosen output states (values) in the lookup table's list. This preserves the reversibility (bijectivity) of the rule.
    *   The number of mutation swaps to apply to each clone should be calculated as `max(1, round(mutation_rate * len(lookup_table)))`. This ensures at least one mutation is applied.
    *   The script must save the generated list of rules to a specified output file.

2.  **Execute the script:**
    *   Find the champion rule file from `iter_179`. Based on past iterations, it is likely named `champion_rule.json` or similar within `archive/iter_179/results/`.
    *   Run `src/create_mutated_population.py` with the following parameters:
        *   `--parent_rule_path`: Path to the `g10_rule_001` rule file from `iter_179`.
        *   `--population_size`: 100
        *   `--mutation_rate`: 0.01 (1%)
        *   `--output_path`: `archive/iter_191/results/warm_start_population.json`

**Success Criterion:**
The file `archive/iter_191/results/warm_start_population.json` is successfully created and contains 100 rule definitions derived from `g10_rule_001`.
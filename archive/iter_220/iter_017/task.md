1. Write a python script src/test_deconstruct_rule.py that:
   - Loads the champion rule 'archive/iter_179/results/champion_rule.json'.
   - Extracts its generator pairs from the rule_dict.
   - Imports '_try_build_c2_rule' and '_rotate_c2' from 'src/evolution.py'.
   - Rebuilds the rule from those pairs.
   - Verifies that the rebuilt rule_dict is exactly identical to the original rule_dict.
2. Run the script and print its output.
3. If successful, print the list of generator pairs that represent the champion rule.
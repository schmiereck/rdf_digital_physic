Write a python script src/test_deconstruct_rule.py that:
1. Loads the champion rule 'archive/iter_179/results/champion_rule.json'.
2. Extracts its generator pairs from the rule_dict.
3. Uses _try_build_c2_rule from src/evolution.py to rebuild the rule from those pairs.
4. Verifies that the rebuilt rule's rule_dict is exactly identical to the original rule_dict.
Print the results.
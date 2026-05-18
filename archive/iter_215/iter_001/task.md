The goal is to create a 'warm-start' population for an evolutionary search. The previous search from a random population (iter_214.3) failed due to a flat fitness landscape. This task will seed the next search with rules known to produce at least *some* form of complex or transient motion, even if they were previously classified as exploits.

1.  Read the champion rules from the following iterations: `iter_213` (the transient drift oscillator), `iter_177` (the transient bloomer), and `iter_153` (the fast puffer). You will need to use `read_iteration` to find the path to the champion rule file for each of these iterations.
2.  Create a new population of 100 rules. The first 3 rules should be the champions you just loaded.
3.  Generate the remaining 97 rules by applying mutations to these 3 seed rules.
4.  Save the resulting population to `archive/iter_215/results/warm_start_population.json`.
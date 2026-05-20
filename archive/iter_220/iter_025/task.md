Create a python script src/search_v2.py that:
1. Searches for any files in the workspace (using os.walk) containing 'v2' or 'warm_start' or 'champion_v2' in their filename.
2. Prints their paths and sizes.
3. Specifically scans the folder 'archive/iter_220/results/' for any files, printing their names and sizes.
4. If 'archive/iter_220/results/champion_v2_rule.json' or any newly created files exist, print their content or summary.
Run the script using 'python src/search_v2.py' and print the complete stdout and stderr.
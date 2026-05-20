Write and run a python script src/diagnose_run.py that:
1. Searches under archive/iter_220/ (and any of its subdirectories) for any files named 'stderr.txt' or 'stdout.txt'.
2. Prints their paths, sizes, and if they contain any error messages or tracebacks, prints those error messages.
This will tell us if run_warm_start_evolution_v2.py failed with a Python exception.
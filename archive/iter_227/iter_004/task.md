Execute a Python one-liner to create the directory `archive/iter_227/results` and run `src/d4_lensing.py`, redirecting the output to `archive/iter_227/results/lensing_test_output.txt`.
You can use a python command like:
`python -c "import os, subprocess; os.makedirs('archive/iter_227/results', exist_ok=True); out = subprocess.check_output(['python', 'src/d4_lensing.py'], text=True); open('archive/iter_227/results/lensing_test_output.txt', 'w').write(out)"`
This is 100% platform-independent and will work on Windows!
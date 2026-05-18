The previous attempt to restore `src/automata_lib` failed. Your task is to copy the directory from `archive/iter_195/src/automata_lib` to `src/automata_lib`.

You can do this by creating and executing a small Python script.

```python
import shutil
import os

source = 'archive/iter_195/src/automata_lib'
destination = 'src/automata_lib'

if os.path.exists(source):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    print(f"Successfully copied {source} to {destination}")
else:
    print(f"Error: Source directory {source} not found.")
    exit(1)

```

Execute this script. Do not perform any other actions. Your success criterion is the existence of the `src/automata_lib` directory after the script runs. Report `status: ok` on success.
import sys
import os
import json

data = {
    "sys_path": sys.path,
    "pythonpath": os.environ.get("PYTHONPATH")
}

print(json.dumps(data, indent=2))

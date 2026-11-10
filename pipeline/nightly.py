import subprocess
import sys
import time

STEPS = [
    ("Load sources", [sys.executable, "pipeline/load.py"], "."),
    ("Snapshot products", ["dbt", "snapshot"], "transform"),
    ("Build and test models", ["dbt", "build"], "transform"),
]

started = time.perf_counter()
for name, command, cwd in STEPS:
    print(f"==> {name}", flush=True)
    if subprocess.run(command, cwd=cwd).returncode != 0:
        sys.exit(f"Nightly run stopped at: {name}")
print(f"Nightly run finished in {time.perf_counter() - started:.0f} s")

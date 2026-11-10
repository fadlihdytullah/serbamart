import argparse
import subprocess
import sys


def run(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, result.stderr, sep="\n")
        sys.exit(f"Failed: {' '.join(command)}")
    return result.stdout


parser = argparse.ArgumentParser(description="Play Serbamart forward day by day: new data, nightly load, product snapshot.")
parser.add_argument("--days", type=int, required=True, help="number of days to add")
parser.add_argument("--issues", default="", help="issues to switch on with the first day, for example price-changes")
args = parser.parse_args()

for i in range(args.days):
    generate = [sys.executable, "systems/generator.py", "next-day"]
    if args.issues and i == 0:
        generate += ["--issues", args.issues]
    day = run(generate).split()[4]
    run([sys.executable, "pipeline/load.py"])
    run(["dbt", "snapshot", "--quiet"], cwd="transform")
    print(f"{day}: loaded and snapshotted")

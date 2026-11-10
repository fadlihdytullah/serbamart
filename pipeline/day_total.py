import csv
import sys
from pathlib import Path


def read_sales(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def revenue(rows):
    return sum(int(row["qty"]) * int(row["unit_price"]) for row in rows)


day = sys.argv[1] if len(sys.argv) > 1 else "2025-11-01"
files = sorted(Path("data/pos").glob(f"*/*_{day}.csv"))

totals = {}
for path in files:
    branch_id = path.stem.split("_")[0]
    totals[branch_id] = revenue(read_sales(path))

for branch_id, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]:
    print(f"{branch_id}  Rp{amount:>11,}".replace(",", "."))
print(f"Files:  {len(files)}")
print(f"Total:  Rp{sum(totals.values()):,}".replace(",", "."))

import sys
from pathlib import Path

from sales import read_sales, rupiah, summarize

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/pos/2025-11-01/BR001_2025-11-01.csv")
try:
    rows, skipped = read_sales(path)
except FileNotFoundError:
    sys.exit(f"No such file: {path}")

summary = summarize(rows)
print(f"File:         {path.name}")
print(f"Revenue:      {rupiah(summary['revenue'])}")
print(f"Transactions: {summary['transactions']}")
print(f"Best seller:  {summary['best_sku']} ({summary['best_sku_units']} units)")
if skipped:
    print(f"Skipped:      {len(skipped)} rows on lines {', '.join(map(str, skipped))}")

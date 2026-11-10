import argparse
import csv
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

from sales import read_sales, rupiah, summarize

parser = argparse.ArgumentParser(description="Summarize one Serbamart branch over a range of days.")
parser.add_argument("branch", help="branch id, for example BR001")
parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True, help="first day, YYYY-MM-DD")
parser.add_argument("--to", dest="end", type=date.fromisoformat, required=True, help="last day, YYYY-MM-DD")
parser.add_argument("--data", default="data", help="data folder (default data)")
parser.add_argument("--csv", type=Path, help="also write the daily rows to this CSV file")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("branch_summary")

if args.end < args.start:
    sys.exit("--to must be on or after --from.")

daily = []
all_rows = []
day = args.start
while day <= args.end:
    files = sorted(Path(args.data, "pos").glob(f"*/{args.branch}_{day}.csv"))
    if not files:
        log.warning("No file for %s on %s", args.branch, day)
    for path in files:
        rows, skipped = read_sales(path)
        summary = summarize(rows)
        daily.append({"day": day.isoformat(), **summary, "skipped_rows": len(skipped)})
        all_rows += rows
    day += timedelta(days=1)

if not daily:
    sys.exit(f"No sales for {args.branch} between {args.start} and {args.end}.")

print(f"{'Day':<12}{'Revenue':>14}{'Trans.':>8}  Best seller")
for row in daily:
    print(f"{row['day']:<12}{rupiah(row['revenue']):>14}{row['transactions']:>8}  {row['best_sku']} ({row['best_sku_units']})")

period = summarize(all_rows)
print()
print(f"{args.branch}, {len(daily)} days")
print(f"Revenue:      {rupiah(period['revenue'])}")
print(f"Per day:      {rupiah(period['revenue'] // len(daily))}")
print(f"Transactions: {period['transactions']}")
print(f"Best seller:  {period['best_sku']} ({period['best_sku_units']} units)")

if args.csv:
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with open(args.csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=daily[0].keys())
        writer.writeheader()
        writer.writerows(daily)
    log.info("Wrote %d rows to %s", len(daily), args.csv)

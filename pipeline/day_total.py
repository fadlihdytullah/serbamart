import argparse
import logging
import sys

from sales import files_for_day, read_sales, rupiah, summarize

parser = argparse.ArgumentParser(description="Total every Serbamart branch for one day.")
parser.add_argument("day", help="sales day, YYYY-MM-DD")
parser.add_argument("--top", type=int, default=5, help="how many branches to list (default 5)")
parser.add_argument("--data", default="data", help="data folder (default data)")
parser.add_argument("--verbose", action="store_true", help="log every file read")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("day_total")

files = files_for_day(args.day, args.data)
if not files:
    sys.exit(f"No sales files for {args.day} in {args.data}/.")

totals = {}
skipped_rows = 0
log.info("Reading %d files for %s from %s/", len(files), args.day, args.data)
for path in files:
    branch_id = path.stem.split("_")[0]
    rows, skipped = read_sales(path)
    totals[branch_id] = summarize(rows)["revenue"]
    skipped_rows += len(skipped)

for branch_id, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)[: args.top]:
    print(f"{branch_id}  {rupiah(amount):>13}")
print(f"Files:  {len(files)}")
print(f"Total:  {rupiah(sum(totals.values()))}")
if skipped_rows:
    log.warning("Skipped %d rows that could not be read", skipped_rows)

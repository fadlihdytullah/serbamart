import sys

from sales import files_for_day, read_sales, rupiah, summarize

day = sys.argv[1] if len(sys.argv) > 1 else "2025-11-01"
files = files_for_day(day)

totals = {}
for path in files:
    branch_id = path.stem.split("_")[0]
    totals[branch_id] = summarize(read_sales(path))["revenue"]

for branch_id, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]:
    print(f"{branch_id}  {rupiah(amount):>13}")
print(f"Files:  {len(files)}")
print(f"Total:  {rupiah(sum(totals.values()))}")

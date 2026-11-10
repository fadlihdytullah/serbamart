import argparse
import logging
import sys
import time
from datetime import date

from load_api import last_closed_day, load_orders, next_day_to_load
from load_files import SOURCES, load_files
from load_masters import load_masters
from online_api import session
from warehouse import connect

parser = argparse.ArgumentParser(description="Load every Serbamart source into the warehouse.")
parser.add_argument("--from", dest="start", type=date.fromisoformat, help="first online order day, needed for the very first load")
parser.add_argument("--verbose", action="store_true", help="log every day loaded from the API")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")

started = time.perf_counter()
con = connect()
s = session()

load_masters(con)
print(f"{'branches, products':<20} full refresh")

for table, pattern in SOURCES.items():
    files, rows = load_files(con, table, pattern)
    print(f"{table:<20} {files:>6} new files {rows:>8} rows")

start = args.start or next_day_to_load(con)
if start is None:
    sys.exit("Nothing loaded from the API yet: pass --from for the first load.")
days, rows = load_orders(con, s, start, last_closed_day())
print(f"{'online_orders':<20} {days:>6} new days  {rows:>8} rows")

checks = {
    "pos_sales": (
        "select count(*) from read_csv('data/pos/*/*.csv', all_varchar = true)",
        "select count(*) from raw.pos_sales",
    ),
    "stock": (
        "select count(*) from read_csv('data/stock/*.csv', all_varchar = true)",
        "select count(*) from raw.stock",
    ),
    "online_orders": (
        """select sum(rows) from (
            select batch, arg_max(rows, loaded_at) as rows
            from raw.load_log where source = 'online_orders' group by batch
        )""",
        "select count(*) from raw.online_orders",
    ),
}

print()
failed = 0
for table, (source_sql, warehouse_sql) in checks.items():
    source = con.execute(source_sql).fetchall()[0][0]
    loaded = con.execute(warehouse_sql).fetchall()[0][0]
    print(f"{'ok' if source == loaded else 'FAIL':<5} {table:<14} source {source:>8}  warehouse {loaded:>8}")
    failed += source != loaded

print(f"\nDone in {time.perf_counter() - started:.1f} s")
if failed:
    sys.exit(f"{failed} table(s) do not match their source.")

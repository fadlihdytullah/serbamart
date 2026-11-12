import argparse
import logging
import sys
import time
from datetime import date

from load_api import last_closed_day, load_orders, next_day_to_load
from load_files import SOURCES, load_files, new_files
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

loaded = {}
for table, pattern in SOURCES.items():
    loaded[table] = new_files(con, table, pattern)
    count, rows = load_files(con, table, pattern, loaded[table])
    print(f"{table:<20} {count:>6} new files {rows:>8} rows")

start = args.start or next_day_to_load(con)
if start is None:
    sys.exit("Nothing loaded from the API yet: pass --from for the first load.")
days, rows = load_orders(con, s, start, last_closed_day())
print(f"{'online_orders':<20} {days:>6} new days  {rows:>8} rows")

checks = []
for table, files in loaded.items():
    if files:
        source = con.execute("select count(*) from read_csv(?, all_varchar = true)", [files]).fetchall()[0][0]
        in_warehouse = con.execute(f"select count(*) from raw.{table} where _source_file in (select unnest(?))", [files]).fetchall()[0][0]
        checks.append((table, source, in_warehouse))

source = con.execute("""
    select sum(rows) from (
        select batch, arg_max(rows, loaded_at) as rows
        from raw.load_log where source = 'online_orders' group by batch
    )
""").fetchall()[0][0]
in_warehouse = con.execute("select count(*) from raw.online_orders").fetchall()[0][0]
checks.append(("online_orders", source, in_warehouse))

print()
failed = 0
for table, source, in_warehouse in checks:
    print(f"{'ok' if source == in_warehouse else 'FAIL':<5} {table:<14} source {source:>8}  warehouse {in_warehouse:>8}")
    failed += source != in_warehouse

print(f"\nDone in {time.perf_counter() - started:.1f} s")
if failed:
    sys.exit(f"{failed} table(s) do not match their source.")

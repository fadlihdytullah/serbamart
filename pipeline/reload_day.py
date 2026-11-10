import argparse
from datetime import date

from load_api import load_orders
from load_files import load_files
from online_api import session
from warehouse import connect

parser = argparse.ArgumentParser(description="Reload one arrival day of Serbamart sources into the warehouse.")
parser.add_argument("day", type=date.fromisoformat, help="arrival day, YYYY-MM-DD")
args = parser.parse_args()

con = connect()
for table, pattern in {"pos_sales": f"data/pos/{args.day}/*.csv", "stock": f"data/stock/{args.day}.csv"}.items():
    files = [row[0] for row in con.execute("select file from glob(?) order by file", [pattern]).fetchall()]
    count, rows = load_files(con, table, pattern, files)
    print(f"{table:<14} {count:>3} files {rows:>6} rows reloaded")

days, rows = load_orders(con, session(), args.day, args.day)
print(f"{'online_orders':<14} {days:>3} day  {rows:>6} rows reloaded")

import sys
from pathlib import Path

import duckdb

con = duckdb.connect("warehouse/serbamart.duckdb", read_only=True)

day = sys.argv[1] if len(sys.argv) > 1 else str(con.execute("select max(sales_date) from marts.mart_daily_sales where channel = 'store'").fetchall()[0][0])

con.execute("""
    create temp table report as
    select branch_id, name, transactions, revenue, avg_7_days, vs_avg_pct, rank
    from marts.mart_branch_daily_sales
    where sales_date = cast(? as date)
    order by rank
""", [day])

branches = con.execute("select count(*) from report").fetchall()[0][0]
if branches == 0:
    sys.exit(f"No sales found for {day}.")
if branches < 30:
    print(f"Warning: only {branches} of 30 branches have sales for {day}; late files may still arrive.")

totals = dict(con.execute("""
    select channel, (sales, revenue)
    from marts.mart_daily_sales
    where sales_date = cast(? as date)
""", [day]).fetchall())
store = totals["store"]
online = totals.get("online", (0, 0))

print(f"Serbamart daily report for {day} (WIB)")
print(f"Store:  {store[0]:>6} transactions  Rp{store[1]:>13,}".replace(",", "."))
print(f"Online: {online[0]:>6} paid orders   Rp{online[1]:>13,}".replace(",", "."))
print()
con.sql("select rank, branch_id, name, revenue, vs_avg_pct from report").show(max_rows=6)

con.sql("""
    select sku, name, units
    from marts.mart_product_daily_sales
    where sales_date = cast(? as date) and channel = 'store'
    order by units desc
    limit 3
""", params=[day]).show()

Path("output/reports").mkdir(parents=True, exist_ok=True)
con.execute(f"copy report to 'output/reports/daily_{day}.csv' (header)")
print(f"Saved output/reports/daily_{day}.csv")

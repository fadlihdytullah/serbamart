import sys
from pathlib import Path

import duckdb

from clean_pos import clean_pos

con = duckdb.connect()
clean_pos(con)
con.sql("set TimeZone = 'Asia/Jakarta'")

day = sys.argv[1] if len(sys.argv) > 1 else str(con.execute("select max(cast(sold_at as date)) from clean").fetchall()[0][0])

con.execute("""
    create table branch_days as
    select branch_id, cast(sold_at as date) as day, count(distinct transaction_id) as transactions, sum(qty * unit_price) as revenue
    from clean
    group by all
""")

con.execute("""
    create table report as
    select
        b.branch_id,
        b.name,
        d.transactions,
        d.revenue,
        d.avg_7_days,
        round((d.revenue - d.avg_7_days) * 100.0 / d.avg_7_days, 1) as vs_avg_pct,
        rank() over (order by d.revenue desc) as rank
    from (
        select
            *,
            cast(avg(revenue) over (partition by branch_id order by day rows between 7 preceding and 1 preceding) as bigint) as avg_7_days
        from branch_days
    ) as d
    join read_csv('data/branches.csv') as b using (branch_id)
    where d.day = cast(? as date)
    order by rank
""", [day])

store = con.execute("select sum(transactions), sum(revenue) from report").fetchall()[0]
online = con.execute("""
    select count(distinct order_id), sum(item.qty * item.unit_price)
    from read_json('data/online/orders/*.jsonl'), unnest(items) as t(item)
    where status = 'paid' and cast(created_at as date) = cast(? as date)
""", [day]).fetchall()[0]

print(f"Serbamart daily report for {day} (WIB)")
print(f"Store:  {store[0]:>6} transactions  Rp{store[1]:>13,}".replace(",", "."))
print(f"Online: {online[0]:>6} paid orders   Rp{online[1]:>13,}".replace(",", "."))
print()
con.sql("select rank, branch_id, name, revenue, vs_avg_pct from report").show(max_rows=6)

con.sql("""
    select c.sku, p.name, sum(c.qty) as units
    from clean as c
    join read_csv('data/products.csv') as p using (sku)
    where cast(c.sold_at as date) = cast(? as date)
    group by all
    order by units desc
    limit 3
""", params=[day]).show()

Path("output/reports").mkdir(parents=True, exist_ok=True)
con.execute(f"copy report to 'output/reports/daily_{day}.csv' (header)")
print(f"Saved output/reports/daily_{day}.csv")

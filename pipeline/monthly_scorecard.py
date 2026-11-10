import argparse
from pathlib import Path

import duckdb

parser = argparse.ArgumentParser(description="Score every Serbamart branch for one month.")
parser.add_argument("month", help="month, YYYY-MM")
args = parser.parse_args()
month = f"{args.month}-01"

con = duckdb.connect("output/serbamart.duckdb", read_only=True)
con.sql("set TimeZone = 'Asia/Jakarta'")

scorecard = con.sql("""
    with monthly as (
        select
            branch_id,
            date_trunc('month', sold_at)::date as month,
            count(distinct transaction_id) as transactions,
            sum(qty * unit_price) as revenue
        from sales
        group by branch_id, month
    ),
    compared as (
        select
            *,
            round((revenue - lag(revenue) over w) * 100.0 / lag(revenue) over w, 1) as vs_last_month_pct
        from monthly
        window w as (partition by branch_id order by month)
    ),
    categories as (
        select
            s.branch_id,
            p.category,
            sum(s.qty * s.unit_price) as revenue,
            row_number() over (partition by s.branch_id order by sum(s.qty * s.unit_price) desc) as position
        from sales as s
        join products as p using (sku)
        where date_trunc('month', s.sold_at)::date = cast($month as date)
        group by s.branch_id, p.category
    )
    select
        rank() over (order by c.revenue desc) as rank,
        b.branch_id,
        b.name,
        c.revenue,
        c.transactions,
        c.revenue // c.transactions as avg_basket,
        c.vs_last_month_pct,
        t.category as top_category
    from compared as c
    join branches as b using (branch_id)
    join categories as t on t.branch_id = c.branch_id and t.position = 1
    where c.month = cast($month as date)
    order by rank
""", params={"month": month})

if not scorecard.fetchall():
    raise SystemExit(f"No sales in {args.month}.")

print(f"Serbamart scorecard for {args.month}")
scorecard.show(max_rows=10)

Path("output/reports").mkdir(parents=True, exist_ok=True)
target = f"output/reports/scorecard_{args.month}.csv"
scorecard.write_csv(target)
print(f"Saved {target}")

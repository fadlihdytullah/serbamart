import time
from pathlib import Path

import duckdb

Path("output").mkdir(exist_ok=True)

duckdb.sql("""
    copy (select * from read_csv('data/pos/*/*.csv'))
    to 'output/pos_sales.parquet' (format parquet)
""")

duckdb.sql("""
    copy (
        select
            o.order_id,
            o.created_at,
            o.city,
            o.status,
            item.sku,
            item.qty,
            item.unit_price
        from read_json('data/online/orders/*.jsonl') as o,
            unnest(o.items) as t(item)
    )
    to 'output/online_order_lines.parquet' (format parquet)
""")

csv_bytes = sum(f.stat().st_size for f in Path("data/pos").rglob("*.csv"))
parquet_bytes = Path("output/pos_sales.parquet").stat().st_size
print(f"POS as CSV:     {csv_bytes / 1_000_000:6.1f} MB")
print(f"POS as Parquet: {parquet_bytes / 1_000_000:6.1f} MB")

for source in ["read_csv('data/pos/*/*.csv')", "'output/pos_sales.parquet'"]:
    start = time.perf_counter()
    duckdb.sql(f"select sum(qty * unit_price) from {source}").fetchall()
    print(f"Revenue query on {source}: {(time.perf_counter() - start) * 1000:.0f} ms")

duckdb.sql("""
    select status, count(distinct order_id) as orders, sum(qty * unit_price) as revenue
    from 'output/online_order_lines.parquet'
    group by status
""").show()

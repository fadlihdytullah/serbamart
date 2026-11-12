import time
from pathlib import Path

import duckdb

Path("output").mkdir(exist_ok=True)
con = duckdb.connect("warehouse/serbamart.duckdb", read_only=True)
files = {"csv": "output/fct_sales.csv", "parquet": "output/fct_sales.parquet"}

for fmt, path in files.items():
    start = time.perf_counter()
    con.sql(f"copy marts.fct_sales to '{path}' (format {fmt})")
    size = Path(path).stat().st_size / 1_000_000
    print(f"{fmt:<8} {size:7.1f} MB  written in {time.perf_counter() - start:5.2f} s")

print()
for fmt, path in files.items():
    start = time.perf_counter()
    rows = con.sql(f"select channel, sum(revenue) as revenue from '{path}' group by channel order by channel").fetchall()
    print(f"{fmt:<8} {rows}  {(time.perf_counter() - start) * 1000:6.0f} ms")

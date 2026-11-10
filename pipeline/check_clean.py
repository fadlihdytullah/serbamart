import sys

import duckdb

RULES = {
    "qty is positive": "qty <= 0",
    "price is positive": "unit_price <= 0",
    "price matches the catalog": "unit_price <> catalog_price",
    "sku is in the catalog": "catalog_price is null",
    "branch exists": "timezone is null",
    "payment method is known": "payment_method not in ('cash', 'qris', 'debit', 'ewallet', 'unknown')",
    "sold during opening hours": "hour(timezone(timezone, sold_at)) not between 7 and 22",
}

con = duckdb.connect()
con.sql("""
    create view checked as
    select s.*, p.unit_price as catalog_price, b.timezone
    from 'output/pos_clean.parquet' as s
    left join read_csv('data/products.csv') as p on p.sku = s.sku
    left join read_csv('data/branches.csv') as b on b.branch_id = s.branch_id
""")

failed = 0
for name, broken in RULES.items():
    bad = con.execute(f"select count(*) from checked where {broken}").fetchall()[0][0]
    print(f"{'FAIL' if bad else 'ok':<5} {name}: {bad} rows")
    failed += bool(bad)

duplicates = con.execute("""
    select count(*) from (
        select transaction_id, sku from checked group by all having count(*) > 1
    )
""").fetchall()[0][0]
print(f"{'FAIL' if duplicates else 'ok':<5} one line per product per transaction: {duplicates} pairs")
failed += bool(duplicates)

if failed:
    sys.exit(f"{failed} rule(s) failed.")
print("All rules passed.")

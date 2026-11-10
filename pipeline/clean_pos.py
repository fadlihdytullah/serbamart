from pathlib import Path

import duckdb

con = duckdb.connect()

con.sql("""
    create table raw as
    select * from read_csv('data/pos/*/*.csv', all_varchar = true)
""")

con.sql("""
    create table clean as
    select distinct
        transaction_id,
        branch_id,
        cast(sold_at as timestamptz) as sold_at,
        sku,
        cast(qty as integer) as qty,
        cast(replace(replace(unit_price, 'Rp', ''), '.', '') as integer) as unit_price,
        coalesce(payment_method, 'unknown') as payment_method
    from raw
    where qty is not null
""")

Path("output").mkdir(exist_ok=True)
con.sql("copy clean to 'output/pos_clean.parquet' (format parquet)")

con.sql("""
    select
        (select count(*) from raw) as raw_rows,
        count(*) as clean_rows,
        sum(qty * unit_price) as revenue
    from clean
""").show()

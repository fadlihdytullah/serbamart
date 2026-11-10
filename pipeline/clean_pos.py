from pathlib import Path

import duckdb

con = duckdb.connect()
con.sql("set TimeZone = 'UTC'")

con.sql("""
    create table raw as
    select * from read_csv('data/pos/*/*.csv', all_varchar = true)
""")

con.sql("""
    create table clean as
    select distinct
        transaction_id,
        raw.branch_id,
        case
            when length(sold_at) > 19 then cast(sold_at as timestamptz)
            else timezone(b.timezone, cast(sold_at as timestamp))
        end as sold_at,
        sku,
        cast(qty as integer) as qty,
        cast(replace(replace(unit_price, 'Rp', ''), '.', '') as integer) as unit_price,
        coalesce(payment_method, 'unknown') as payment_method
    from raw
    join read_csv('data/branches.csv') as b using (branch_id)
    where qty is not null
""")

Path("output").mkdir(exist_ok=True)
con.sql("copy clean to 'output/pos_clean.parquet' (format parquet)")

con.sql("""
    select
        cast(timezone('Asia/Jakarta', sold_at) as date) as sales_date_wib,
        count(*) as rows,
        sum(qty * unit_price) as revenue
    from clean
    where timezone('Asia/Jakarta', sold_at) >= '2026-11-01'
    group by all
    order by sales_date_wib
""").show()

con.sql("""
    select
        (select count(*) from raw) as raw_rows,
        count(*) as clean_rows,
        sum(qty * unit_price) as revenue
    from clean
""").show()

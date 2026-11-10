import duckdb

con = duckdb.connect()

con.sql("""
    create table stock as
    select
        cast(parse_filename(filename, true) as date) as day,
        branch_id,
        sku,
        on_hand
    from read_csv('data/stock/*.csv', filename = true)
""")

con.sql("""
    create table sold as
    select
        cast(timezone(b.timezone, s.sold_at) as date) as day,
        s.branch_id,
        s.sku,
        sum(s.qty) as units
    from 'output/pos_clean.parquet' as s
    join read_csv('data/branches.csv') as b using (branch_id)
    group by all
""")

con.sql("""
    create table reconciled as
    select
        today.day,
        today.branch_id,
        today.sku,
        case when yesterday.on_hand < 15 then 80 else yesterday.on_hand end as opening,
        coalesce(sold.units, 0) as sold,
        today.on_hand as closing,
        opening - coalesce(sold.units, 0) - today.on_hand as unexplained
    from stock as today
    join stock as yesterday
        on yesterday.branch_id = today.branch_id
        and yesterday.sku = today.sku
        and yesterday.day = today.day - 1
    left join sold
        on sold.branch_id = today.branch_id
        and sold.sku = today.sku
        and sold.day = today.day
""")

con.sql("""
    select
        day,
        count(*) filter (where unexplained <> 0) as mismatches,
        sum(unexplained) as missing_units
    from reconciled
    where day > (select max(day) from reconciled) - 14
    group by day
    order by day
""").show()

con.sql("""
    select day, branch_id, sku, opening, sold, closing, unexplained
    from reconciled
    where unexplained <> 0
    order by day, branch_id, sku
    limit 8
""").show()

import duckdb

con = duckdb.connect()

con.sql("""
    create table raw as
    select * from read_csv('data/pos/*/*.csv', all_varchar = true, filename = true)
""")

con.sql("""
    select
        count(*) as rows,
        count(*) - (select count(*) from (select distinct * exclude (filename) from raw)) as duplicate_rows,
        count(*) filter (where qty is null) as missing_qty,
        count(*) filter (where payment_method is null) as missing_payment,
        count(*) filter (where qty like '%.%') as odd_qty,
        count(*) filter (where try_cast(unit_price as integer) is null) as odd_price
    from raw
""").show()

con.sql("""
    select unit_price, count(*) as rows
    from raw
    where try_cast(unit_price as integer) is null
    group by unit_price
    order by rows desc
    limit 5
""").show()

con.sql("""
    select
        replace(split_part(parse_filename(filename), '_', 2), '.csv', '') as sales_day,
        count(*) as rows,
        count(*) filter (where qty is null or payment_method is null or qty like '%.%'
                         or try_cast(unit_price as integer) is null) as problem_rows
    from raw
    group by sales_day
    order by sales_day desc
    limit 5
""").show()

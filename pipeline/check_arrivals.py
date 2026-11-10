import duckdb

con = duckdb.connect()

con.sql("""
    create table arrivals as
    select
        cast(split_part(file, '/', 3) as date) as arrived_on,
        split_part(parse_filename(file, true), '_', 1) as branch_id,
        cast(split_part(parse_filename(file, true), '_', 2) as date) as sales_day
    from glob('data/pos/*/*.csv')
""")

con.sql("""
    select branch_id, sales_day, arrived_on, arrived_on - sales_day as days_late
    from arrivals
    where arrived_on > sales_day
    order by sales_day
""").show()

con.sql("""
    with days as (
        select distinct sales_day from arrivals
        where sales_day > (select max(sales_day) from arrivals) - 7
    ),
    expected as (
        select d.sales_day, b.branch_id
        from days as d
        cross join read_csv('data/branches.csv') as b
    )
    select
        e.sales_day,
        count(a.branch_id) as files,
        string_agg(e.branch_id, ', ') filter (where a.branch_id is null) as missing
    from expected as e
    left join arrivals as a using (sales_day, branch_id)
    group by e.sales_day
    order by e.sales_day
""").show()

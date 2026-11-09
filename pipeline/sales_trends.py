import duckdb

con = duckdb.connect()
con.sql("set TimeZone = 'Asia/Jakarta'")
con.sql("create view sales as select * from 'output/pos_clean.parquet'")

con.sql("""
    select branch_id, sku, units, rank
    from (
        select
            branch_id,
            sku,
            sum(qty) as units,
            rank() over (partition by branch_id order by sum(qty) desc) as rank
        from sales
        group by branch_id, sku
    )
    where rank <= 3 and branch_id in ('BR001', 'BR030')
    order by branch_id, rank
""").show()

con.sql("""
    with monthly as (
        select date_trunc('month', sold_at)::date as month, sum(qty * unit_price) as revenue
        from sales
        group by month
    )
    select
        month,
        revenue,
        sum(revenue) over (order by month) as running_total
    from monthly
    order by month
""").show(max_rows=14)

con.sql("""
    with daily as (
        select cast(sold_at as date) as day, sum(qty * unit_price) as revenue
        from sales
        group by day
    )
    select
        day,
        revenue,
        revenue - lag(revenue) over (order by day) as change,
        cast(avg(revenue) over (order by day rows between 6 preceding and current row) as bigint) as avg_7_days
    from daily
    order by day desc
    limit 7
""").show()

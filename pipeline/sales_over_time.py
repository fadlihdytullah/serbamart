import duckdb

con = duckdb.connect("output/serbamart.duckdb", read_only=True)
con.sql("set TimeZone = 'Asia/Jakarta'")

con.sql("""
    select
        date_trunc('month', sold_at)::date as month,
        count(distinct transaction_id) as transactions,
        sum(qty * unit_price) as revenue
    from sales
    group by month
    order by month
""").show(max_rows=12)

con.sql("""
    select
        isodow(sold_at) as day_number,
        dayname(sold_at) as day,
        sum(qty * unit_price) // count(distinct cast(sold_at as date)) as revenue_per_day
    from sales
    group by day_number, day
    order by day_number
""").show()

con.sql("""
    select
        hour(sold_at) as hour,
        count(distinct transaction_id) as transactions,
        bar(count(distinct transaction_id), 0, 40000, 30) as chart
    from sales
    group by hour
    order by hour
""").show(max_rows=20)

import duckdb

con = duckdb.connect()
con.sql("create view sales as select * from 'output/pos_sales.parquet'")
con.sql("create view branches as select * from read_csv('data/branches.csv')")
con.sql("create view products as select * from read_csv('data/products.csv')")
con.sql("create view online as select * from 'output/online_order_lines.parquet'")

con.sql("""
    select
        b.city,
        count(distinct b.branch_id) as branches,
        sum(s.qty * s.unit_price) as store_revenue,
        sum(s.qty * s.unit_price) // count(distinct b.branch_id) as per_branch
    from sales as s
    join branches as b on b.branch_id = s.branch_id
    group by b.city
    order by per_branch desc
""").show(max_rows=6)

con.sql("""
    select
        b.city,
        p.category,
        sum(s.qty) as units
    from sales as s
    join branches as b on b.branch_id = s.branch_id
    join products as p on p.sku = s.sku
    where b.city = 'Jayapura'
    group by b.city, p.category
    order by units desc
""").show()

con.sql("""
    select p.sku, p.name, count(o.sku) as online_lines
    from products as p
    left join online as o
        on o.sku = p.sku and o.city = 'Jayapura' and o.created_at < '2025-11-08'
    group by p.sku, p.name
    order by online_lines, p.sku
    limit 8
""").show()

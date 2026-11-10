import duckdb

sales_by_branch = duckdb.sql("""
    select
        b.branch_id,
        b.name,
        count(distinct s.transaction_id) as transactions,
        sum(s.qty * s.unit_price) as revenue
    from read_csv('data/pos/*/*.csv') as s
    join read_csv('data/branches.csv') as b using (branch_id)
    group by b.branch_id, b.name
    order by revenue desc
""")

sales_by_branch.show(max_rows=10)

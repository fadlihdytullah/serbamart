import duckdb

con = duckdb.connect("output/serbamart.duckdb", read_only=True)

con.sql("""
    with baskets as (
        select
            branch_id,
            transaction_id,
            count(*) as lines,
            sum(qty) as items,
            sum(qty * unit_price) as amount
        from sales
        group by branch_id, transaction_id
    ),
    per_branch as (
        select
            branch_id,
            count(*) as transactions,
            round(avg(items), 2) as avg_items,
            cast(avg(amount) as bigint) as avg_amount
        from baskets
        group by branch_id
    )
    select b.name, p.transactions, p.avg_items, p.avg_amount
    from per_branch as p
    join branches as b using (branch_id)
    order by p.avg_amount desc
""").show(max_rows=6)

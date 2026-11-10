import duckdb

con = duckdb.connect("output/serbamart.duckdb")

con.sql("create or replace table sales as select * from 'output/pos_sales.parquet'")
con.sql("create or replace table online_order_lines as select * from 'output/online_order_lines.parquet'")
con.sql("create or replace table branches as select * from read_csv('data/branches.csv')")
con.sql("create or replace table products as select * from read_csv('data/products.csv')")

con.sql("""
    select table_name, estimated_size as rows
    from duckdb_tables()
    order by table_name
""").show()

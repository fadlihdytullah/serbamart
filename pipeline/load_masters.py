from warehouse import connect


def load_masters(con):
    for table in ["branches", "products"]:
        con.sql(f"""
            create or replace table raw.{table} as
            select *, current_timestamp as _loaded_at
            from read_csv('data/{table}.csv', all_varchar = true)
        """)


if __name__ == "__main__":
    con = connect()
    load_masters(con)
    con.sql("""
        select schema_name, table_name, estimated_size as rows
        from duckdb_tables()
        order by all
    """).show()

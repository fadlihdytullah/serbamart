from warehouse import connect

SOURCES = {
    "pos_sales": "data/pos/*/*.csv",
    "stock": "data/stock/*.csv",
}


def load_files(con, table, pattern):
    con.sql(f"""
        create table if not exists raw.{table} as
        select * rename (filename as _source_file), current_timestamp as _loaded_at
        from read_csv('{pattern}', all_varchar = true, filename = true)
        limit 0
    """)
    con.begin()
    try:
        con.sql(f"""
            delete from raw.{table}
            where _source_file in (select file from glob('{pattern}'))
        """)
        con.sql(f"""
            insert into raw.{table} by name
            select * rename (filename as _source_file), current_timestamp as _loaded_at
            from read_csv('{pattern}', all_varchar = true, filename = true)
        """)
        con.commit()
    except Exception:
        con.rollback()
        raise


if __name__ == "__main__":
    con = connect()
    for table, pattern in SOURCES.items():
        load_files(con, table, pattern)
    con.sql("""
        select 'pos_sales' as table_name, count(*) as rows, count(distinct _source_file) as files from raw.pos_sales
        union all
        select 'stock', count(*), count(distinct _source_file) from raw.stock
    """).show()

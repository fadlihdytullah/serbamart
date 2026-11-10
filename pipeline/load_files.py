import time

from warehouse import connect

SOURCES = {
    "pos_sales": "data/pos/*/*.csv",
    "stock": "data/stock/*.csv",
}


def new_files(con, table, pattern):
    return [row[0] for row in con.execute("""
        select file from glob(?)
        where file not in (select batch from raw.load_log where source = ?)
        order by file
    """, [pattern, table]).fetchall()]


def load_files(con, table, pattern, files=None):
    if files is None:
        files = new_files(con, table, pattern)
    if not files:
        return 0, 0
    con.sql(f"""
        create table if not exists raw.{table} as
        select * rename (filename as _source_file), current_timestamp as _loaded_at
        from read_csv('{pattern}', all_varchar = true, filename = true)
        limit 0
    """)
    con.begin()
    try:
        con.execute(f"delete from raw.{table} where _source_file in (select unnest(?))", [files])
        con.execute(f"""
            insert into raw.{table} by name
            select * rename (filename as _source_file), current_timestamp as _loaded_at
            from read_csv(?, all_varchar = true, filename = true)
        """, [files])
        con.execute(f"""
            insert into raw.load_log
            select ?, f.file, count(t._source_file), current_timestamp
            from (select unnest(?) as file) as f
            left join raw.{table} as t on t._source_file = f.file
            group by f.file
        """, [table, files])
        con.commit()
    except Exception:
        con.rollback()
        raise
    rows = con.execute(f"select count(*) from raw.{table} where _source_file in (select unnest(?))", [files]).fetchall()[0][0]
    return len(files), rows


if __name__ == "__main__":
    con = connect()
    for table, pattern in SOURCES.items():
        start = time.perf_counter()
        files, rows = load_files(con, table, pattern)
        print(f"{table:<10} {files:>6} new files {rows:>8} rows  {time.perf_counter() - start:.2f} s")

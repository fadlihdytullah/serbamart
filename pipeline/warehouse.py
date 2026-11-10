from pathlib import Path

import duckdb

WAREHOUSE = Path("warehouse/serbamart.duckdb")


def connect():
    WAREHOUSE.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    con.sql("create schema if not exists raw")
    con.sql("""
        create table if not exists raw.load_log (
            source varchar,
            batch varchar,
            rows bigint,
            loaded_at timestamptz
        )
    """)
    return con

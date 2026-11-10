from pathlib import Path

import duckdb

WAREHOUSE = Path("warehouse/serbamart.duckdb")


def connect():
    WAREHOUSE.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    con.sql("create schema if not exists raw")
    return con

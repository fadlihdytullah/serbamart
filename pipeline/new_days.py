import sys
from pathlib import Path

import duckdb

con = duckdb.connect("warehouse/serbamart.duckdb", read_only=True)
loaded = {row[0] for row in con.execute("select batch from raw.load_log where source = 'stock'").fetchall()}
waiting = sorted(str(path) for path in Path("data/stock").glob("*.csv") if str(path) not in loaded)
for path in waiting:
    print(path)
sys.exit(0 if waiting else 1)

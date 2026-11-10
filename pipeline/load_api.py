import argparse
import json
import logging
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from online_api import fetch_orders, session
from warehouse import connect

log = logging.getLogger("load_api")


def last_closed_day():
    return max(date.fromisoformat(path.stem) for path in Path("data/stock").glob("*.csv"))


def next_day_to_load(con):
    last = con.execute("select max(batch) from raw.load_log where source = 'online_orders'").fetchall()[0][0]
    return date.fromisoformat(last) + timedelta(days=1) if last else None


def load_orders(con, s, start, end):
    con.sql("""
        create table if not exists raw.online_orders (
            order_id varchar primary key,
            order_date date,
            payload json,
            _loaded_at timestamptz
        )
    """)
    days = rows = 0
    day = start
    while day <= end:
        orders = fetch_orders(s, day, page_size=500)
        con.begin()
        try:
            con.execute("""
                merge into raw.online_orders as target
                using (
                    select payload ->> 'order_id' as order_id, ?::date as order_date, payload
                    from (select unnest(?)::json as payload)
                ) as source
                on target.order_id = source.order_id
                when matched then update set payload = source.payload, _loaded_at = current_timestamp
                when not matched then insert values (source.order_id, source.order_date, source.payload, current_timestamp)
            """, [day, [json.dumps(order) for order in orders]])
            con.execute("insert into raw.load_log values ('online_orders', ?, ?, current_timestamp)", [str(day), len(orders)])
            con.commit()
        except Exception:
            con.rollback()
            raise
        log.info("%s: %d orders", day, len(orders))
        days += 1
        rows += len(orders)
        day += timedelta(days=1)
    return days, rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load online store orders into the Serbamart warehouse.")
    parser.add_argument("--from", dest="start", type=date.fromisoformat, help="first day, default the day after the last load")
    parser.add_argument("--to", dest="end", type=date.fromisoformat, help="last day, default the last day the stores closed")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    con = connect()
    start = args.start or next_day_to_load(con)
    if start is None:
        sys.exit("Nothing loaded yet: pass --from for the first load.")
    end = args.end or last_closed_day()
    if start > end:
        print(f"Up to date: orders are loaded through {end}.")
        sys.exit()

    started = time.perf_counter()
    days, rows = load_orders(con, session(), start, end)
    print(f"Loaded {rows} orders over {days} days in {time.perf_counter() - started:.0f} s")

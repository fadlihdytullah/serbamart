import argparse
import logging
import os
import sys
import time
from datetime import date, timedelta

import requests

from sales import rupiah

BASE_URL = os.environ.get("SERBAMART_API_URL", "http://127.0.0.1:8000")

log = logging.getLogger("online_api")


def session():
    key = os.environ.get("SERBAMART_API_KEY")
    if not key:
        sys.exit("Set SERBAMART_API_KEY first.")
    s = requests.Session()
    s.headers["X-API-Key"] = key
    return s


def get_page(s, params, tries=5):
    for attempt in range(1, tries + 1):
        try:
            response = s.get(f"{BASE_URL}/orders", params=params, timeout=10)
        except (requests.ConnectionError, requests.Timeout) as error:
            wait, reason = 2 ** attempt, type(error).__name__
        else:
            if response.status_code == 429:
                wait, reason = int(response.headers["Retry-After"]), "429 Too Many Requests"
            elif response.status_code >= 500:
                wait, reason = 2 ** attempt, f"{response.status_code} {response.reason}"
            else:
                response.raise_for_status()
                return response.json()
        if attempt < tries:
            log.warning("%s on %s page %s, retry %d in %d s", reason, params["date"], params["page"], attempt, wait)
            time.sleep(wait)
    raise RuntimeError(f"Gave up on {params['date']} page {params['page']} after {tries} tries: {reason}")


def fetch_orders(s, day, page_size=100):
    orders = []
    page = 1
    while page:
        body = get_page(s, {"date": day, "page": page, "page_size": page_size})
        orders += body["data"]
        page = body["next_page"]
    return orders


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch orders from the Serbamart online store API.")
    parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True, help="first order day in WIB, YYYY-MM-DD")
    parser.add_argument("--to", dest="end", type=date.fromisoformat, help="last order day, default the same as --from")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    s = session()
    day = args.start
    total = 0
    started = time.perf_counter()
    while day <= (args.end or args.start):
        orders = fetch_orders(s, day)
        paid = [o for o in orders if o["status"] == "paid"]
        revenue = sum(item["qty"] * item["unit_price"] for o in paid for item in o["items"])
        log.info("%s: %d orders, %d paid, %s", day, len(orders), len(paid), rupiah(revenue))
        total += len(orders)
        day += timedelta(days=1)
    log.info("%d orders in %.0f s", total, time.perf_counter() - started)

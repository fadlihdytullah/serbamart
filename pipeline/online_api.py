import argparse
import os
import sys
from datetime import date

import requests

from sales import rupiah

BASE_URL = os.environ.get("SERBAMART_API_URL", "http://127.0.0.1:8000")


def session():
    key = os.environ.get("SERBAMART_API_KEY")
    if not key:
        sys.exit("Set SERBAMART_API_KEY first.")
    s = requests.Session()
    s.headers["X-API-Key"] = key
    return s


def fetch_orders(s, day, page_size=100):
    orders = []
    page = 1
    while page:
        response = s.get(f"{BASE_URL}/orders", params={"date": day, "page": page, "page_size": page_size}, timeout=10)
        response.raise_for_status()
        body = response.json()
        orders += body["data"]
        page = body["next_page"]
    return orders


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch one day of orders from the Serbamart online store API.")
    parser.add_argument("day", type=date.fromisoformat, help="order day in WIB, YYYY-MM-DD")
    args = parser.parse_args()

    orders = fetch_orders(session(), args.day)
    paid = [o for o in orders if o["status"] == "paid"]
    revenue = sum(item["qty"] * item["unit_price"] for o in paid for item in o["items"])
    print(f"{args.day}: {len(orders)} orders, {len(paid)} paid, {rupiah(revenue)}")
    print(orders[0])

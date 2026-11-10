import csv
from pathlib import Path


def read_sales(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows):
    revenue = 0
    transactions = set()
    units_by_sku = {}
    for row in rows:
        qty = int(row["qty"])
        revenue += qty * int(row["unit_price"])
        transactions.add(row["transaction_id"])
        units_by_sku[row["sku"]] = units_by_sku.get(row["sku"], 0) + qty
    best_sku = max(units_by_sku, key=units_by_sku.get)
    return {
        "revenue": revenue,
        "transactions": len(transactions),
        "best_sku": best_sku,
        "best_sku_units": units_by_sku[best_sku],
    }


def files_for_day(day, data_dir="data"):
    return sorted(Path(data_dir, "pos").glob(f"*/*_{day}.csv"))


def rupiah(amount):
    return f"Rp{amount:,}".replace(",", ".")

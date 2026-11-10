import csv
import sys
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


path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/pos/2025-11-01/BR001_2025-11-01.csv")
summary = summarize(read_sales(path))
print(f"File:         {path.name}")
print(f"Revenue:      Rp{summary['revenue']:,}".replace(",", "."))
print(f"Transactions: {summary['transactions']}")
print(f"Best seller:  {summary['best_sku']} ({summary['best_sku_units']} units)")

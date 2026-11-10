import csv
from pathlib import Path


def read_sales(path):
    rows = []
    skipped = []
    with open(path, newline="") as f:
        for line_number, row in enumerate(csv.DictReader(f), start=2):
            try:
                row["qty"] = int(row["qty"])
                row["unit_price"] = int(row["unit_price"])
            except ValueError:
                skipped.append(line_number)
                continue
            rows.append(row)
    return rows, skipped


def summarize(rows):
    revenue = 0
    transactions = set()
    units_by_sku = {}
    for row in rows:
        qty = row["qty"]
        revenue += qty * row["unit_price"]
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

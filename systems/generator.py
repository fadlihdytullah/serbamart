import argparse
import csv
import json
import random
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ISSUES = ("duplicates", "nulls", "bad-types", "timezones", "late-files", "price-changes")

CITIES = [
    ("Jakarta", 7, 5), ("Bandung", 7, 4), ("Bekasi", 7, 2), ("Bogor", 7, 2), ("Depok", 7, 1),
    ("Tangerang", 7, 2), ("Semarang", 7, 2), ("Yogyakarta", 7, 2), ("Surabaya", 7, 3), ("Malang", 7, 1),
    ("Medan", 7, 2), ("Palembang", 7, 1), ("Denpasar", 8, 1), ("Makassar", 8, 1), ("Jayapura", 9, 1),
]
TZ_NAMES = {7: "Asia/Jakarta", 8: "Asia/Makassar", 9: "Asia/Jayapura"}

PRODUCTS = [
    ("Air Mineral 600ml", "Minuman", 3500), ("Air Mineral 1500ml", "Minuman", 6500),
    ("Teh Manis Botol 350ml", "Minuman", 4500), ("Kopi Susu Botol 220ml", "Minuman", 8000),
    ("Minuman Isotonik 500ml", "Minuman", 7500), ("Jus Jeruk Kotak 250ml", "Minuman", 6000),
    ("Mi Instan Goreng", "Makanan Instan", 3500), ("Mi Instan Kuah Ayam", "Makanan Instan", 3200),
    ("Bubur Instan", "Makanan Instan", 6500), ("Sarden Kaleng 155g", "Makanan Instan", 12500),
    ("Nugget Ayam 500g", "Makanan Instan", 38000), ("Beras 5kg", "Sembako", 72000),
    ("Gula Pasir 1kg", "Sembako", 18500), ("Minyak Goreng 2L", "Sembako", 38500),
    ("Tepung Terigu 1kg", "Sembako", 13500), ("Garam 250g", "Sembako", 4000),
    ("Kecap Manis 520ml", "Sembako", 22000), ("Susu UHT Cokelat 1L", "Susu & Telur", 19500),
    ("Susu UHT Plain 250ml", "Susu & Telur", 6500), ("Telur Ayam 10 Butir", "Susu & Telur", 29000),
    ("Yoghurt Stroberi 200ml", "Susu & Telur", 9500), ("Roti Tawar", "Roti & Snack", 13500),
    ("Roti Sobek Cokelat", "Roti & Snack", 16000), ("Keripik Kentang 68g", "Roti & Snack", 11000),
    ("Biskuit Kelapa 300g", "Roti & Snack", 15500), ("Wafer Cokelat", "Roti & Snack", 9000),
    ("Kacang Atom 250g", "Roti & Snack", 14000), ("Cokelat Batang 62g", "Roti & Snack", 12000),
    ("Sabun Mandi Batang", "Perawatan Diri", 4500), ("Sampo Sachet", "Perawatan Diri", 1000),
    ("Pasta Gigi 190g", "Perawatan Diri", 14500), ("Sikat Gigi", "Perawatan Diri", 9000),
    ("Deodoran 50ml", "Perawatan Diri", 24000), ("Tisu Wajah 250 Lembar", "Rumah Tangga", 13000),
    ("Deterjen Bubuk 800g", "Rumah Tangga", 21000), ("Sabun Cuci Piring 780ml", "Rumah Tangga", 16500),
    ("Pembersih Lantai 800ml", "Rumah Tangga", 15000), ("Baterai AA isi 2", "Rumah Tangga", 18000),
    ("Kantong Sampah", "Rumah Tangga", 9000), ("Obat Nyamuk Bakar", "Rumah Tangga", 6500),
]
SKUS = [f"SM-{i + 1:04d}" for i in range(len(PRODUCTS))]
SKU_WEIGHTS = [1 / price ** 0.5 for _, _, price in PRODUCTS]

HOURS = list(range(7, 23))
HOUR_WEIGHTS = [3, 5, 5, 4, 5, 7, 6, 4, 4, 5, 7, 8, 7, 5, 3, 2]
PAYMENTS = ["cash", "qris", "debit", "ewallet"]
PAYMENT_WEIGHTS = [40, 30, 15, 15]
QTYS = [1, 2, 3, 4, 6]
QTY_WEIGHTS = [60, 22, 9, 5, 4]

POS_FIELDS = ["transaction_id", "branch_id", "sold_at", "sku", "qty", "unit_price", "payment_method"]
RESTOCK_BELOW, RESTOCK_TO = 15, 80


def branches():
    rows, n = [], 0
    for city, offset, count in CITIES:
        for i in range(count):
            n += 1
            rows.append({
                "branch_id": f"BR{n:03d}",
                "name": f"Serbamart {city} {i + 1}",
                "city": city,
                "timezone": TZ_NAMES[offset],
                "opened_on": (date(2019, 1, 7) + timedelta(days=53 * n)).isoformat(),
                "_offset": offset,
            })
    return rows


def price_on(idx, day, state):
    base = PRODUCTS[idx][2]
    since = state.get("price_changes_since")
    if not since or day < date.fromisoformat(since):
        return base, None
    period = 40 + (idx * 7) % 60
    steps = (day - date.fromisoformat(since)).days // period
    if steps == 0:
        return base, None
    return round(base * 1.04 ** steps / 100) * 100, date.fromisoformat(since) + timedelta(days=steps * period)


def pos_rows(state, branch, day, prices, stock):
    rng = random.Random(f"{state['seed']}:pos:{day}:{branch['branch_id']}")
    tz = timezone(timedelta(hours=branch["_offset"]))
    count = max(1, round(rng.randint(20, 40) * (1.3 if day.weekday() >= 5 else 1) * state["scale"]))
    times = sorted(
        (rng.choices(HOURS, HOUR_WEIGHTS)[0], rng.randrange(60), rng.randrange(60)) for _ in range(count)
    )
    rows = []
    for n, (h, m, s) in enumerate(times, 1):
        sold_at = datetime(day.year, day.month, day.day, h, m, s, tzinfo=tz)
        payment = rng.choices(PAYMENTS, PAYMENT_WEIGHTS)[0]
        picked = {rng.choices(range(len(SKUS)), SKU_WEIGHTS)[0] for _ in range(rng.randint(1, 4))}
        for idx in sorted(picked):
            qty = rng.choices(QTYS, QTY_WEIGHTS)[0]
            key = f"{branch['branch_id']}|{SKUS[idx]}"
            qty = min(qty, stock[key])
            if qty == 0:
                continue
            stock[key] -= qty
            rows.append({
                "transaction_id": f"{branch['branch_id']}-{day:%Y%m%d}-{n:05d}",
                "branch_id": branch["branch_id"],
                "sold_at": sold_at.isoformat(),
                "sku": SKUS[idx],
                "qty": qty,
                "unit_price": prices[idx],
                "payment_method": payment,
            })
    return rows


def add_issues(rows, issues, rng):
    out = []
    for row in rows:
        row = dict(row)
        if "timezones" in issues:
            row["sold_at"] = row["sold_at"][:19]
        if "nulls" in issues:
            roll = rng.random()
            if roll < 0.01:
                row["payment_method"] = ""
            elif roll < 0.013:
                row["qty"] = ""
        if "bad-types" in issues:
            roll = rng.random()
            if roll < 0.01:
                row["unit_price"] = "Rp" + f"{row['unit_price']:,}".replace(",", ".")
            elif roll < 0.02 and row["qty"] != "":
                row["qty"] = f"{row['qty']}.0"
        out.append(row)
        if "duplicates" in issues and rng.random() < 0.01:
            out.append(dict(row))
    return out


def online_orders(state, day, prices):
    rng = random.Random(f"{state['seed']}:online:{day}")
    cities = [c for c, _, _ in CITIES]
    weights = [w for _, _, w in CITIES]
    count = max(1, round(rng.randint(60, 120) * state["scale"]))
    orders = []
    for n in range(1, count + 1):
        local = datetime(day.year, day.month, day.day, rng.randint(6, 23), rng.randrange(60), rng.randrange(60),
                         tzinfo=timezone(timedelta(hours=7)))
        picked = {rng.choices(range(len(SKUS)), SKU_WEIGHTS)[0] for _ in range(rng.randint(1, 5))}
        orders.append({
            "order_id": f"WEB-{day:%Y%m%d}-{n:05d}",
            "created_at": local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "customer_id": f"C{rng.randint(1, round(5000 * state['scale'])):06d}",
            "city": rng.choices(cities, weights)[0],
            "status": "cancelled" if rng.random() < 0.08 else "paid",
            "items": [
                {"sku": SKUS[i], "qty": rng.choices(QTYS, QTY_WEIGHTS)[0], "unit_price": prices[i]}
                for i in sorted(picked)
            ],
        })
    return orders


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate_day(out, state, day, branch_rows):
    issues = set(state["issues"])
    priced = [price_on(i, day, state) for i in range(len(PRODUCTS))]
    prices = [p for p, _ in priced]
    stock = state["stock"]

    for key, have in stock.items():
        if have < RESTOCK_BELOW * state["scale"]:
            stock[key] = round(RESTOCK_TO * state["scale"])

    arrived = out / ".outbox" / day.isoformat()
    if arrived.exists():
        target = out / "pos" / day.isoformat()
        target.mkdir(parents=True, exist_ok=True)
        for f in sorted(arrived.iterdir()):
            f.rename(target / f.name)
        arrived.rmdir()

    for branch in branch_rows:
        rows = pos_rows(state, branch, day, prices, stock)
        rng = random.Random(f"{state['seed']}:issues:{day}:{branch['branch_id']}")
        rows = add_issues(rows, issues, rng)
        delay = rng.randint(1, 3) if "late-files" in issues and rng.random() < 0.04 else 0
        folder = out / ".outbox" / (day + timedelta(days=delay)).isoformat() if delay else out / "pos" / day.isoformat()
        write_csv(folder / f"{branch['branch_id']}_{day}.csv", POS_FIELDS, rows)

    write_csv(out / "stock" / f"{day}.csv", ["branch_id", "sku", "on_hand"], [
        {"branch_id": k.split("|")[0], "sku": k.split("|")[1], "on_hand": v} for k, v in stock.items()
    ])

    orders_file = out / "online" / "orders" / f"{day}.jsonl"
    orders_file.parent.mkdir(parents=True, exist_ok=True)
    orders_file.write_text("".join(json.dumps(o) + "\n" for o in online_orders(state, day, prices)))

    write_csv(out / "products.csv", ["sku", "name", "category", "unit_price", "updated_on"], [
        {"sku": SKUS[i], "name": name, "category": cat, "unit_price": priced[i][0],
         "updated_on": (priced[i][1] or date.fromisoformat(state["start"])).isoformat()}
        for i, (name, cat, _) in enumerate(PRODUCTS)
    ])
    state["last_day"] = day.isoformat()


def parse_issues(text):
    if not text:
        return []
    chosen = list(ISSUES) if text == "all" else [i.strip() for i in text.split(",")]
    unknown = [i for i in chosen if i not in ISSUES]
    if unknown:
        sys.exit(f"Unknown issue: {', '.join(unknown)}. Choose from: {', '.join(ISSUES)}, or all.")
    return chosen


def enable_issues(state, chosen, day):
    for issue in chosen:
        if issue not in state["issues"]:
            state["issues"].append(issue)
            if issue == "price-changes":
                state["price_changes_since"] = day.isoformat()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Serbamart data.")
    sub = parser.add_subparsers(dest="command", required=True)
    hist = sub.add_parser("history", help="write a past period at once")
    hist.add_argument("--start", default="2025-11-01")
    hist.add_argument("--days", type=int, default=365)
    hist.add_argument("--scale", type=float, default=1.0)
    hist.add_argument("--seed", type=int, default=42)
    nxt = sub.add_parser("next-day", help="add one new day after the last one")
    for p in (hist, nxt):
        p.add_argument("--issues", default="", help=f"comma list of {', '.join(ISSUES)}, or all")
        p.add_argument("--out", default="data")
    args = parser.parse_args(argv)

    out = Path(args.out)
    state_file = out / ".state.json"
    branch_rows = branches()

    if args.command == "history":
        if state_file.exists():
            sys.exit(f"{out} already has data. Delete it first, or use next-day.")
        start = date.fromisoformat(args.start)
        state = {"seed": args.seed, "scale": args.scale, "start": start.isoformat(), "issues": [],
                 "stock": {f"{b['branch_id']}|{s}": round(RESTOCK_TO * args.scale) for b in branch_rows for s in SKUS}}
        enable_issues(state, parse_issues(args.issues), start)
        out.mkdir(parents=True, exist_ok=True)
        write_csv(out / "branches.csv", ["branch_id", "name", "city", "timezone", "opened_on"], branch_rows)
        days = [start + timedelta(days=d) for d in range(args.days)]
    else:
        if not state_file.exists():
            sys.exit(f"No data in {out}. Run history first.")
        state = json.loads(state_file.read_text())
        day = date.fromisoformat(state["last_day"]) + timedelta(days=1)
        enable_issues(state, parse_issues(args.issues), day)
        days = [day]

    for day in days:
        generate_day(out, state, day, branch_rows)
    state_file.write_text(json.dumps(state))
    print(f"Serbamart data up to {state['last_day']} in {out}/ (issues: {', '.join(state['issues']) or 'none'})")


if __name__ == "__main__":
    main()

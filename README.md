# Serbamart

Data for Serbamart, a fictional 30-branch minimarket chain used in the suikodev Data Engineer path. Not a real brand.

## Generate

```sh
uv run generator.py history
uv run generator.py next-day
```

`history` writes one year (2025-11-01 to 2026-10-31) into `data/`. `next-day` adds the day after the last one.

Options: `--scale 10` for ten times the rows, `--seed`, `--start`, `--days`, `--out`, and `--issues` to switch on messy data (comma list or `all`):

| Issue           | What changes                                                  |
| --------------- | ------------------------------------------------------------- |
| `duplicates`    | about 1% of POS rows appear twice                             |
| `nulls`         | empty `payment_method` and `qty`                              |
| `bad-types`     | prices like `Rp12.500`, quantities like `2.0`                 |
| `timezones`     | `sold_at` loses its offset and stays in the branch's local time |
| `late-files`    | about 4% of branch files arrive one to three days late        |
| `price-changes` | product prices rise over time, `products.csv` follows         |

Issues stay on once enabled. The same seed always gives the same data, and issues never change the underlying sales.

## Output

```
data/
  branches.csv
  products.csv                              current prices
  pos/<arrival-date>/<branch>_<sales-date>.csv
  stock/<date>.csv                          end-of-day stock per branch
  online/orders/<date>.jsonl                web shop orders, UTC
```

## Test

```sh
uv run python -m unittest discover tests
```

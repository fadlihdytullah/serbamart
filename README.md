# Serbamart

Serbamart is a fictional 30-branch minimarket chain used in the suikodev Data Engineer path. Not a real brand.

- `systems/` is the company's side, already built by its dev team: a data generator and the online store API. You use them, you don't change them.
- `pipeline/` is your side: the code you write part by part. Each part has a tag (`<series-id>/part-N`, for example `python-for-data/part-3`) so you can compare your work or jump ahead. Stage 1 series in order: `python-for-data`, `sql-analytics-on-files`, `cleaning-messy-data`.

## Generate data

```sh
uv run systems/generator.py history
uv run systems/generator.py next-day
```

`history` writes one year (2025-11-01 to 2026-10-31) into `data/`. `next-day` adds the day after the last one.

Options: `--scale 10` for ten times the rows, `--seed`, `--start`, `--days`, `--out`, and `--issues` to switch on messy data (comma list or `all`):

| Issue           | What changes                                                    |
| --------------- | --------------------------------------------------------------- |
| `duplicates`    | about 1% of POS rows appear twice                               |
| `nulls`         | empty `payment_method` and `qty`                                |
| `bad-types`     | prices like `Rp12.500`, quantities like `2.0`                   |
| `timezones`     | `sold_at` loses its offset and stays in the branch's local time |
| `late-files`    | about 4% of branch files arrive one to three days late          |
| `price-changes` | product prices rise over time, `products.csv` follows           |

Issues stay on once enabled. The same seed always gives the same data, and issues never change the underlying sales.

```
data/
  branches.csv
  products.csv                              current prices
  pos/<arrival-date>/<branch>_<sales-date>.csv
  stock/<date>.csv                          end-of-day stock per branch; the warehouse refills a product to 80 at opening when it closed below 15
  online/orders/<date>.jsonl                web shop orders, served by the API
```

## Online store API

```sh
uv run systems/api.py
```

Docs at http://localhost:8000/docs. Send `X-API-Key: serbamart-dev-key`.

| Endpoint             | Returns                                                          |
| -------------------- | ---------------------------------------------------------------- |
| `GET /orders?date=`  | one day of orders, `page` and `page_size` (max 500), `next_page` |
| `GET /orders/{id}`   | one order                                                        |
| `GET /health`        | `{"status": "ok"}`, no key needed                                |

Settings by environment variable: `SERBAMART_DATA` (default `data`), `SERBAMART_API_KEY`, `SERBAMART_RATE_LIMIT` (requests per minute, default 60, then 429 with `Retry-After`), `SERBAMART_FLAKY` (share of requests that fail with 503, default 0), `HOST` (default `127.0.0.1`), `PORT`.

## Test

```sh
uv run python -m unittest discover tests
```

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

## Run the pipeline in Airflow

```sh
docker compose up -d
```

| Service   | URL                   | What it does                                       |
| --------- | --------------------- | -------------------------------------------------- |
| Airflow   | http://localhost:8080 | `serbamart_nightly` at 01:00 WIB, `serbamart_freshness` every hour, `serbamart_reload` for backfills, `serbamart_stores` closes one more day |
| API       | http://localhost:8000 | the online store API                               |
| Dashboard | http://localhost:8501 | the Streamlit sales dashboard                      |
| Mailpit   | http://localhost:8025 | alert emails from failed tasks, each with a runbook link |

DuckDB allows one writer, and its lock does not reach from your machine into the containers. While Compose is up, change the warehouse only through Airflow, or run commands inside it: `docker compose exec airflow-scheduler bash`, then `cd /opt/serbamart`. Stop everything with `docker compose down`.

When a task fails, its runbook in `docs/runbooks/` says what to check, how to fix it and how to rerun.

`serbamart_nightly` has a time budget: when a run is not finished 300 minutes after it was queued (06:00 WIB for the 01:00 run), an email goes to Mailpit with the `deadline` runbook. Change it with `SERBAMART_NIGHTLY_BUDGET_MINUTES=<minutes> docker compose up -d`. The Fernet key in `compose.yaml` is for this local setup only.

## Exports and docs

Every `dbt build` writes `fct_sales` as Parquet to `exports/fct_sales/date_day=<day>/`, one folder per business day, for tools that should not open the warehouse.

`uv run pipeline/timings.py` lists the slowest models and tests of the last dbt run. For the lineage graph, with the dashboard, the daily report and the finance export as exposures:

```sh
cd transform
uv run dbt docs generate
uv run dbt docs serve --port 8081
```

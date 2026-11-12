# build_models

`dbt build` stopped: a test with severity error failed, or a contract no longer matches. Models downstream of the failure were skipped, so the marts and the dashboard still show the last good night.

Owner: the `meta.owner` of the failing model in `transform/models/*.yml` (data, merchandising or operations).

## Check

1. Open the log from the alert and find the `FAIL` or `ERROR` line. It names the test or the model.
2. Failing rows are kept in the `audit` schema, one table per test:

```bash
docker compose exec -w /opt/serbamart airflow-scheduler /home/airflow/serbamart/bin/python -c "import duckdb; print(duckdb.connect('warehouse/serbamart.duckdb', read_only=True).sql('select * from audit.<test name>'))"
```

## Fix

- Bad source rows (a price of 0, an unknown branch): the file is wrong. Ask the branch for a corrected file, put it in place, and reload its arrival day:

```bash
docker compose exec -w /opt/serbamart airflow-scheduler /home/airflow/serbamart/bin/python pipeline/reload_day.py <day>
```

- Contract error: a model changed its columns. Fix the model or the contract in a pull request, never in the night.
- Never lower a test to `warn` to get the night through.

## Rerun

```bash
docker compose exec airflow-scheduler airflow tasks clear serbamart_nightly -t build_models -d -f -y
```

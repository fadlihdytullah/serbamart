# daily_report

`pipeline/daily_report.py` failed after the models were built.

Owner: data team.

## Check

1. `No sales found for <day>`: the marts have no store sales for the last day, usually because every file for it is late.
2. Any other error: read the traceback in the log.

## Rerun

The warehouse is already up to date, so only the report runs again:

```bash
docker compose exec airflow-scheduler airflow tasks clear serbamart_nightly -t daily_report -f -y
```

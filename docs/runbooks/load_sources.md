# load_sources

`pipeline/load.py` failed after every retry, or a warehouse count did not match its source.

Owner: data team.

## Check

1. Open the log from the alert. The last lines name the source.
2. `503` or `Gave up on ... after 5 tries`: the online store API is down. `curl -s localhost:8000/health`.
3. `FAIL <table>`: a file changed after it was loaded, or a load stopped halfway.

## Fix

- API down: wait for it, or ask the web shop team. Nothing to clean: finished days are in `raw.load_log`, the next try starts after them.
- Count mismatch: reload the arrival day, it replaces that day's files and orders:

```bash
docker compose exec -w /opt/serbamart airflow-scheduler /home/airflow/serbamart/bin/python pipeline/reload_day.py <day>
```

## Rerun

```bash
docker compose exec airflow-scheduler airflow tasks clear serbamart_nightly -t load_sources -d -f -y
```

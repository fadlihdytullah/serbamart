# stores_closed

The nightly run waited six hours and no store closed a new day.

Owner: operations (branch systems), data team on call.

## Check

1. `ls data/stock | tail -3` shows the last day the stores sent.
2. Is `serbamart_stores` paused, or did its last run fail? Look in the Airflow UI.

## Fix

- Stores late: wait. The next nightly run picks the day up.
- `serbamart_stores` failed: read its log, fix it, trigger it again.

## Rerun

Clear `stores_closed` with its downstream tasks in the failed run:

```bash
docker compose exec airflow-scheduler airflow tasks clear serbamart_nightly -t stores_closed -d -f -y
```

# deadline

`serbamart_nightly` was not finished within its time budget: `SERBAMART_NIGHTLY_BUDGET_MINUTES` after the run was queued, 300 minutes by default, so 06:00 WIB for the 01:00 run. The head office opens the dashboard at 06:00 and still sees the day before.

Owner: data team on call.

## Check

1. Open the run in the Airflow UI and find the task that is still running or waiting.
2. `stores_closed` still waiting: the stores have not sent the day yet, see [stores_closed](stores_closed.md).
3. Another task running long: compare its duration with earlier runs, and list the slowest dbt nodes:

```bash
docker compose exec -w /opt/serbamart airflow-scheduler /home/airflow/serbamart/bin/python pipeline/timings.py
```

## Fix

- Stores late: nothing to fix in the pipeline. Tell the head office the numbers come later.
- A slow step: find the node that grew and fix it in a pull request, not in the night (a view read by many models, a full rebuild that could be incremental).

## Rerun

None. The alert does not stop the run; it finishes on its own.

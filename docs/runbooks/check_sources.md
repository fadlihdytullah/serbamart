# check_sources

`dbt source freshness` found a source that was not loaded for more than 50 hours (`error_after` in `transform/models/staging/sources.yml`). The nightly run has not loaded anything for two nights.

Owner: data team.

## Check

1. Is `serbamart_nightly` paused, or are its last runs failed or still waiting in `stores_closed`? Look in the Airflow UI.
2. The freshness log lists each source with the age of its newest `_loaded_at`.

## Fix

Follow the runbook of the nightly task that failed. Once the nightly run loads again, the next hourly check passes on its own.

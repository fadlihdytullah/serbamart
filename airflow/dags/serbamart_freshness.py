from datetime import datetime

from airflow.sdk import dag, task

from alerts import alert

SERBAMART = "/opt/serbamart"
VENV = "/home/airflow/serbamart/bin"


@dag(
    schedule="0 * * * *",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"on_failure_callback": alert},
    tags=["serbamart"],
)
def serbamart_freshness():
    @task.bash(cwd=f"{SERBAMART}/transform", pool="warehouse")
    def check_sources():
        return f"{VENV}/dbt source freshness"

    check_sources()


serbamart_freshness()

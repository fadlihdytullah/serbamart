from datetime import datetime

from airflow.sdk import dag, task

SERBAMART = "/opt/serbamart"
VENV = "/home/airflow/serbamart/bin"


@dag(
    schedule="@daily",
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2026, 10, 31),
    catchup=False,
    max_active_runs=1,
    tags=["serbamart"],
)
def serbamart_reload():
    @task.bash(cwd=SERBAMART, pool="warehouse")
    def reload_day(logical_date=None):
        day = logical_date.in_timezone("Asia/Jakarta").date()
        return f"{VENV}/python pipeline/reload_day.py {day}"

    @task.bash(cwd=f"{SERBAMART}/transform", pool="warehouse")
    def build_models(logical_date=None):
        day = logical_date.in_timezone("Asia/Jakarta").date()
        return f"{VENV}/dbt build --vars '{{from_day: {day}}}'"

    reload_day() >> build_models()


serbamart_reload()

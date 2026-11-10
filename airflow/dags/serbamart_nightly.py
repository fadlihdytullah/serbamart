from datetime import datetime

from airflow.sdk import dag, task

SERBAMART = "/opt/serbamart"
VENV = "/home/airflow/serbamart/bin"


@dag(schedule=None, start_date=datetime(2026, 11, 1), catchup=False, tags=["serbamart"])
def serbamart_nightly():
    @task.bash(cwd=SERBAMART)
    def load_sources():
        return f"{VENV}/python pipeline/load.py"

    load_sources()


serbamart_nightly()

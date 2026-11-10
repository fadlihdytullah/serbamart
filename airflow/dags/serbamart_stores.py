from datetime import datetime

from airflow.sdk import dag, task

SERBAMART = "/opt/serbamart"
VENV = "/home/airflow/serbamart/bin"


@dag(schedule=None, start_date=datetime(2026, 11, 1), catchup=False, tags=["serbamart"])
def serbamart_stores():
    @task.bash(cwd=SERBAMART)
    def close_the_day():
        return f"{VENV}/python systems/generator.py next-day"

    close_the_day()


serbamart_stores()

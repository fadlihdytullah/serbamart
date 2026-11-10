from datetime import datetime

from airflow.sdk import dag, task


@dag(schedule=None, start_date=datetime(2026, 11, 1), catchup=False, tags=["serbamart"])
def hello():
    @task
    def count_branches():
        return 30

    @task
    def report(branches):
        print(f"Serbamart has {branches} branches")

    report(count_branches())


hello()

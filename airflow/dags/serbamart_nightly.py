import subprocess
from datetime import datetime, timedelta

from airflow.providers.smtp.notifications.smtp import SmtpNotifier
from airflow.sdk import dag, task

SERBAMART = "/opt/serbamart"
VENV = "/home/airflow/serbamart/bin"

alert = SmtpNotifier(
    from_email="airflow@serbamart.example",
    to="data-team@serbamart.example",
    subject="[Serbamart] {{ ti.task_id }} failed on {{ dag.dag_id }}",
    html_content=(
        "<p>Task <b>{{ ti.task_id }}</b> failed after {{ ti.try_number }} attempt(s).</p>"
        '<p><a href="{{ ti.log_url }}">Open the log</a></p>'
    ),
)


@dag(
    schedule="0 1 * * *",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(seconds=30),
        "retry_exponential_backoff": 2.0,
        "execution_timeout": timedelta(minutes=30),
        "on_failure_callback": alert,
    },
    tags=["serbamart"],
)
def serbamart_nightly():
    @task.sensor(poke_interval=60, timeout=timedelta(hours=6), mode="reschedule", pool="warehouse")
    def stores_closed():
        result = subprocess.run([f"{VENV}/python", "pipeline/new_days.py"], cwd=SERBAMART, capture_output=True, text=True)
        print(result.stdout or "No new day yet")
        return result.returncode == 0

    @task.bash(cwd=SERBAMART, pool="warehouse")
    def load_sources():
        return f"{VENV}/python pipeline/load.py"

    @task.bash(cwd=f"{SERBAMART}/transform", pool="warehouse", retries=0)
    def build_models():
        return f"{VENV}/dbt build"

    @task.bash(cwd=SERBAMART, pool="warehouse")
    def daily_report():
        return f"{VENV}/python pipeline/daily_report.py"

    stores_closed() >> load_sources() >> build_models() >> daily_report()


serbamart_nightly()

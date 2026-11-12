from airflow.providers.smtp.notifications.smtp import SmtpNotifier
from airflow.sdk import AsyncCallback

alert = SmtpNotifier(
    from_email="airflow@serbamart.example",
    to="data-team@serbamart.example",
    subject="[Serbamart] {{ ti.task_id }} failed on {{ dag.dag_id }}",
    html_content=(
        "<p>Task <b>{{ ti.task_id }}</b> failed after {{ ti.try_number }} attempt(s).</p>"
        '<p><a href="{{ ti.log_url }}">Open the log</a></p>'
        '<p><a href="https://github.com/fadlihdytullah/serbamart/blob/main/docs/runbooks/{{ ti.task_id }}.md">Runbook</a></p>'
    ),
)

late = AsyncCallback(
    SmtpNotifier,
    kwargs={
        "from_email": "airflow@serbamart.example",
        "to": "data-team@serbamart.example",
        "subject": "[Serbamart] {{ dag_run.dag_id }} missed its deadline",
        "html_content": (
            "<p>The run queued at {{ dag_run.queued_at }} was not finished by {{ deadline.deadline_time }}.</p>"
            '<p><a href="https://github.com/fadlihdytullah/serbamart/blob/main/docs/runbooks/deadline.md">Runbook</a></p>'
        ),
    },
)

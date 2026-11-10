FROM apache/airflow:3.4.0-python3.14
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
COPY pyproject.toml uv.lock /tmp/serbamart/
RUN cd /tmp/serbamart && UV_PROJECT_ENVIRONMENT=/home/airflow/serbamart uv sync --frozen --no-dev --no-install-project

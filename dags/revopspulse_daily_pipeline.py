from __future__ import annotations

from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator
from airflow.sdk import DAG

default_args = {
    "owner": "revopspulse",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="revopspulse_daily_pipeline",
    description="Daily ELT pipeline for RevOpsPulse SaaS revenue analytics.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["revopspulse", "postgres", "api", "events", "raw", "dbt"],
) as dag:
    extract_postgres_sources = BashOperator(
        task_id="extract_postgres_sources",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/postgres_extractor.py "
            "--output-root /opt/airflow/project/raw"
        ),
        env={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "revopspulse",
            "POSTGRES_USER": "revopspulse",
            "POSTGRES_PASSWORD": "revopspulse",
        },
        append_env=True,
    )

    extract_api_sources = BashOperator(
        task_id="extract_api_sources",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/api_extractor.py "
            "--base-url http://mock-crm-api:8000 "
            "--output-root /opt/airflow/project/raw "
            "--page-size 10 "
            "--updated-since 2026-02-01T00:00:00Z"
        ),
        append_env=True,
    )

    load_api_raw_json = BashOperator(
        task_id="load_api_raw_json",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/raw_json_loader.py "
            "--input-root /opt/airflow/project/raw/api"
        ),
        env={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "revopspulse",
            "POSTGRES_USER": "revopspulse",
            "POSTGRES_PASSWORD": "revopspulse",
        },
        append_env=True,
    )

    generate_product_events = BashOperator(
        task_id="generate_product_events",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/generators/generate_product_events.py "
            "--output-dir /opt/airflow/project/data/product_events "
            "--start-date 2026-01-01 "
            "--days 120 "
            "--seed 42"
        ),
        append_env=True,
    )

    extract_product_events = BashOperator(
        task_id="extract_product_events",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/events_extractor.py "
            "--input-dir /opt/airflow/project/data/product_events "
            "--output-root /opt/airflow/project/raw "
            "--updated-since 2026-02-01T00:00:00Z"
        ),
        append_env=True,
    )

    load_product_events_raw_json = BashOperator(
        task_id="load_product_events_raw_json",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/raw_json_loader.py "
            "--input-root /opt/airflow/project/raw/events"
        ),
        env={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "revopspulse",
            "POSTGRES_USER": "revopspulse",
            "POSTGRES_PASSWORD": "revopspulse",
        },
        append_env=True,
    )

    extract_api_sources >> load_api_raw_json
    generate_product_events >> extract_product_events >> load_product_events_raw_json

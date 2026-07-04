# Runbook

This runbook explains how to start, run, validate and troubleshoot the RevOpsPulse local analytics pipeline.

## Purpose

RevOpsPulse is a local modern data stack project for SaaS revenue, retention, product usage, marketing ROI and sales commission analytics.

The pipeline uses:

- Docker Compose
- PostgreSQL
- Airflow
- Python extractors
- Mock CRM API
- Product event generator
- dbt
- dbt snapshots
- dbt incremental models

## Prerequisites

Required tools:

| Tool | Purpose |
|---|---|
| Docker Desktop | Runs Postgres, mock API and Airflow |
| Docker Compose | Starts the local stack |
| Git | Version control |
| Python 3 | Optional local development and scripts |

The project is designed to run primarily through Docker to avoid local Python dependency issues.

## Repository Setup

From the project root:

`cd /Users/giian/revopspulse-modern-data-stack`

Check Git status:

`git status --short`

The working tree should be clean before running validation or publishing evidence.

## Start the Local Stack

Start all services:

`docker compose up -d`

Check running containers:

`docker ps`

Expected services:

| Container | Purpose |
|---|---|
| `revopspulse-postgres` | Source database, Airflow metadata database and analytics database |
| `revopspulse-mock-crm-api` | Mock CRM and marketing API |
| `revopspulse-airflow-webserver` | Airflow API server and UI |
| `revopspulse-airflow-scheduler` | Airflow scheduler |
| `revopspulse-airflow-dag-processor` | Airflow DAG parser |
| `revopspulse-airflow-init` | One-time Airflow metadata initialization |

## Check Service Health

Check Postgres:

`docker exec revopspulse-postgres pg_isready -U revopspulse -d revopspulse`

Check mock API:

`curl http://localhost:8000/health`

Check Airflow DAG list:

`docker exec revopspulse-airflow-scheduler airflow dags list | grep revopspulse_daily_pipeline`

## Main Airflow DAG

DAG name:

`revopspulse_daily_pipeline`

The DAG performs the following tasks:

| Task | Purpose |
|---|---|
| `extract_postgres_sources` | Extract OLTP source tables to raw CSV files |
| `extract_api_sources` | Extract paginated CRM and marketing API data to raw JSONL files |
| `load_api_raw_json` | Load API raw JSON records into `raw.json_records` |
| `generate_product_events` | Generate deterministic synthetic product events |
| `extract_product_events` | Extract product events to raw JSONL files |
| `load_product_events_raw_json` | Load product event raw JSON into `raw.json_records` |
| `dbt_snapshot` | Run dbt subscription snapshot |
| `dbt_build` | Run full dbt build |

## Trigger the Pipeline

Generate a unique run ID:

`RUN_ID="manual_validation_$(date -u +%Y%m%dT%H%M%SZ)"`

Trigger the DAG:

`docker exec revopspulse-airflow-scheduler airflow dags trigger -r "$RUN_ID" revopspulse_daily_pipeline`

Wait for completion:

`sleep 150`

## Validate Airflow Run State

Check DAG run state:

`docker exec revopspulse-postgres psql -U revopspulse -d airflow -c "select dag_id, run_id, state, start_date, end_date from dag_run where dag_id = 'revopspulse_daily_pipeline' order by start_date desc limit 5;"`

Expected result:

`state = success`

Check task states:

`docker exec revopspulse-postgres psql -U revopspulse -d airflow -c "select task_id, state, try_number, start_date, end_date from task_instance where dag_id = 'revopspulse_daily_pipeline' order by start_date desc limit 20;"`

Expected result:

All task states should be `success`.

## Run dbt Manually

Manual dbt runs are useful for development and debugging.

Run full dbt build:

`docker run --rm --network revopspulse-modern-data-stack_default -v "$PWD/dbt:/usr/app" -w /usr/app -e DEBIAN_FRONTEND=noninteractive -e PIP_ROOT_USER_ACTION=ignore -e POSTGRES_HOST=postgres -e POSTGRES_PORT=5432 -e POSTGRES_DB=revopspulse -e POSTGRES_USER=revopspulse -e POSTGRES_PASSWORD=revopspulse python:3.12-slim sh -c "set -e && apt-get update >/dev/null && apt-get install -y --no-install-recommends git >/dev/null && pip install --no-cache-dir dbt-postgres==1.9.0 >/dev/null && dbt build --profiles-dir /usr/app"`

Expected result:

`ERROR=0`

Known warnings are expected from intentionally seeded synthetic data quality issues.

## Validate Final Analytics Relations

Run:

`docker exec revopspulse-postgres psql -U revopspulse -d revopspulse -c "select table_schema, table_name, table_type from information_schema.tables where table_schema in ('analytics', 'snapshots') and (table_name like 'dim_%' or table_name like 'fact_%' or table_name like 'mart_%' or table_name = 'subscription_snapshot') order by table_schema, table_name;"`

Expected final relations:

| Relation | Expected Type |
|---|---|
| `analytics.dim_accounts` | View |
| `analytics.dim_customers` | View |
| `analytics.dim_sales_reps` | View |
| `analytics.fact_opportunities` | View |
| `analytics.fact_payments` | View |
| `analytics.fact_product_events` | Base table |
| `analytics.mart_data_quality_summary` | View |
| `analytics.mart_marketing_roi_monthly` | View |
| `analytics.mart_product_usage_daily` | View |
| `analytics.mart_revenue_monthly` | View |
| `analytics.mart_sales_commissions_monthly` | View |
| `snapshots.subscription_snapshot` | Base table |

## Validate Final Mart Counts

Run:

`docker exec revopspulse-postgres psql -U revopspulse -d revopspulse -c "select 'mart_revenue_monthly' as model_name, count(*) as row_count from analytics.mart_revenue_monthly union all select 'mart_product_usage_daily', count(*) from analytics.mart_product_usage_daily union all select 'mart_marketing_roi_monthly', count(*) from analytics.mart_marketing_roi_monthly union all select 'mart_sales_commissions_monthly', count(*) from analytics.mart_sales_commissions_monthly union all select 'mart_data_quality_summary', count(*) from analytics.mart_data_quality_summary union all select 'subscription_snapshot', count(*) from snapshots.subscription_snapshot order by model_name;"`

Latest validated row counts:

| Model | Rows |
|---|---:|
| `mart_data_quality_summary` | 4 |
| `mart_marketing_roi_monthly` | 33 |
| `mart_product_usage_daily` | 89 |
| `mart_revenue_monthly` | 6 |
| `mart_sales_commissions_monthly` | 18 |
| `subscription_snapshot` | 15 |

## Validate Executive Metrics

Run:

`docker exec revopspulse-postgres psql -U revopspulse -d revopspulse -c "select 'revenue' as metric_area, sum(net_revenue)::numeric(12,2) as value_1, sum(mrr)::numeric(12,2) as value_2, sum(churned_accounts)::numeric(12,2) as value_3 from analytics.mart_revenue_monthly union all select 'product_usage', sum(total_events)::numeric(12,2), round(avg(active_accounts), 2), round(avg(core_feature_adoption_rate), 4) from analytics.mart_product_usage_daily union all select 'marketing_roi', sum(marketing_spend)::numeric(12,2), sum(closed_won_revenue)::numeric(12,2), round(avg(marketing_roi), 4) from analytics.mart_marketing_roi_monthly union all select 'sales_commissions', sum(commissionable_revenue)::numeric(12,2), sum(commission_payout)::numeric(12,2), round(avg(commission_accuracy_rate), 4) from analytics.mart_sales_commissions_monthly;"`

Latest validated metrics:

| Metric Area | Value 1 | Value 2 | Value 3 |
|---|---:|---:|---:|
| `revenue` | 4681.75 net revenue | 7099.00 total MRR | 1.00 churned accounts |
| `product_usage` | 1842.00 events | 12.48 avg active accounts | 0.3408 avg core feature adoption |
| `marketing_roi` | 21420.00 spend | 28725.00 closed-won revenue | 0.0896 avg ROI |
| `sales_commissions` | 196.00 commissionable revenue | 9.80 commission payout | 0.1074 avg accuracy rate |

## Data Quality Warnings

The full dbt build is expected to complete with warnings caused by intentional synthetic data quality issues.

Expected warning examples:

| Test | Expected Failed Records | Purpose |
|---|---:|---|
| `valid_subscription_period` | 1 | Demonstrates subscription date validation |
| `amount_non_negative` on `fact_payments.net_paid_amount` | 1 | Demonstrates monetary anomaly detection |
| `refund_not_greater_than_payment` | 1 | Demonstrates refund validation |

These warnings are summarized in `mart_data_quality_summary`.

## Troubleshooting

### Docker Is Not Running

Symptom:

`Cannot connect to the Docker daemon`

Fix:

Start Docker Desktop and rerun:

`docker compose up -d`

### Postgres Is Not Healthy

Check logs:

`docker logs revopspulse-postgres --tail 100`

Restart Postgres:

`docker compose restart postgres`

### Mock API Is Not Healthy

Check logs:

`docker logs revopspulse-mock-crm-api --tail 100`

Test endpoint:

`curl http://localhost:8000/health`

### Airflow DAG Does Not Appear

Check DAG processor logs:

`docker logs revopspulse-airflow-dag-processor --tail 200`

Check DAG list:

`docker exec revopspulse-airflow-scheduler airflow dags list`

### Airflow Task Failed

Check task states from metadata:

`docker exec revopspulse-postgres psql -U revopspulse -d airflow -c "select dag_id, run_id, task_id, state, try_number, start_date, end_date from task_instance where dag_id = 'revopspulse_daily_pipeline' order by start_date desc limit 20;"`

Check scheduler logs:

`docker logs revopspulse-airflow-scheduler --tail 300`

### dbt Build Failed

Run dbt manually with the full dbt command from this runbook.

Common checks:

- confirm Postgres is healthy;
- confirm `POSTGRES_HOST=postgres` inside Docker;
- confirm `dbt/profiles.yml` exists locally;
- confirm raw JSON records exist in `raw.json_records`;
- inspect failing model or test in the dbt output.

### Known Airflow Container Warning

The Airflow containers may show pip dependency resolver warnings related to protobuf packages.

The latest validated pipeline completed successfully despite these warnings.

This should be cleaned up later with a custom Airflow image, but it is not blocking the MVP.

## Stop the Stack

Stop containers:

`docker compose stop`

Stop and remove containers:

`docker compose down`

Do not remove volumes unless intentionally resetting all local data.

## Reset Warning

Avoid running destructive commands such as:

`docker compose down -v`

This deletes Postgres volumes and removes the local databases.

Only use it when intentionally resetting the entire environment.

## Evidence Checklist

Before publishing or sharing the project, capture evidence for:

- successful Airflow DAG run;
- successful `dbt build`;
- final analytics relations;
- final mart counts;
- executive metrics snapshot;
- data quality summary;
- dbt docs if generated;
- dashboard screenshots if available;
- GitHub Actions run if CI/CD is enabled.

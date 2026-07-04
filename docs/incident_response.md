# Incident Response

This document describes how to detect, triage, investigate and resolve incidents in the RevOpsPulse local analytics pipeline.

## Purpose

RevOpsPulse is a local MVP, but it still follows operational practices expected in production analytics engineering work.

The goal of this document is to make failures diagnosable and recoverable.

## Incident Categories

| Category | Examples |
|---|---|
| Orchestration | Airflow DAG failed, task retries exhausted, DAG not scheduled |
| Ingestion | Postgres extractor failed, API extractor failed, events extractor failed |
| RAW loading | JSON records did not load into `raw.json_records` |
| dbt build | Model failed, test failed, snapshot failed |
| Data quality | Known or unexpected data anomalies |
| Freshness | Source data did not update as expected |
| Environment | Docker, Postgres, Airflow or mock API unavailable |
| Documentation mismatch | Docs no longer match implemented models or metrics |

## Severity Levels

| Severity | Definition | Example |
|---|---|---|
| SEV1 | Pipeline unavailable or final marts cannot be built | `dbt_build` fails and marts are missing |
| SEV2 | Pipeline completes but key metrics are wrong or incomplete | Revenue mart row count drops unexpectedly |
| SEV3 | Known quality warning or non-blocking anomaly | Expected synthetic warning appears in dbt |
| SEV4 | Documentation or cosmetic issue | Runbook command needs clarification |

## Detection

Primary detection methods:

| Signal | How to Check |
|---|---|
| Airflow DAG state | Query `dag_run` in the Airflow metadata database |
| Airflow task state | Query `task_instance` in the Airflow metadata database |
| dbt build result | Inspect dbt output for `ERROR=0` |
| Final mart counts | Query final mart row counts |
| Data quality status | Query `mart_data_quality_summary` |
| Service health | Check Docker container status and service endpoints |

## First Response Checklist

When an incident occurs:

1. Identify the failing stage.
2. Capture the exact error message.
3. Check whether Git working tree is clean.
4. Check Docker container health.
5. Check Airflow task state.
6. Check dbt output if the failure is model-related.
7. Query final mart counts.
8. Decide whether the issue is code, data, environment or documentation.
9. Apply the smallest safe fix.
10. Re-run the narrowest validation first.
11. Re-run full validation after the fix.

## Useful Commands

### Check Git State

`git status --short`

Expected:

No output.

### Check Containers

`docker ps`

Expected containers:

- `revopspulse-postgres`
- `revopspulse-mock-crm-api`
- `revopspulse-airflow-webserver`
- `revopspulse-airflow-scheduler`
- `revopspulse-airflow-dag-processor`

### Check Postgres

`docker exec revopspulse-postgres pg_isready -U revopspulse -d revopspulse`

Expected:

`accepting connections`

### Check Mock API

`curl http://localhost:8000/health`

Expected:

`status = ok`

## Airflow Incident Response

### Symptom: DAG Does Not Appear

Check DAG list:

`docker exec revopspulse-airflow-scheduler airflow dags list`

Check DAG processor logs:

`docker logs revopspulse-airflow-dag-processor --tail 200`

Common causes:

| Cause | Fix |
|---|---|
| Python syntax error in DAG | Run local syntax check and fix DAG |
| DAG processor not running | Restart Airflow services |
| Wrong DAG folder | Confirm `AIRFLOW__CORE__DAGS_FOLDER` points to `/opt/airflow/project/dags` |

### Symptom: DAG Run Failed

Query recent DAG runs:

`docker exec revopspulse-postgres psql -U revopspulse -d airflow -c "select dag_id, run_id, state, start_date, end_date from dag_run where dag_id = 'revopspulse_daily_pipeline' order by start_date desc limit 5;"`

Query task states:

`docker exec revopspulse-postgres psql -U revopspulse -d airflow -c "select task_id, state, try_number, start_date, end_date from task_instance where dag_id = 'revopspulse_daily_pipeline' order by start_date desc limit 20;"`

Next step:

Investigate the first failed task by timestamp.

## Ingestion Incident Response

### Symptom: Postgres Extraction Failed

Likely task:

`extract_postgres_sources`

Checks:

- confirm Postgres container is healthy;
- confirm `POSTGRES_HOST=postgres` inside Airflow;
- confirm source tables exist under `source` schema;
- check extractor logs.

Manual test:

`python src/ingestion/postgres_extractor.py --output-root raw`

### Symptom: API Extraction Failed

Likely task:

`extract_api_sources`

Checks:

- confirm mock API container is healthy;
- test `/health`;
- test a paginated endpoint;
- confirm base URL is `http://mock-crm-api:8000` inside Docker.

Manual test from host:

`curl "http://localhost:8000/opportunities?page=1&page_size=3"`

### Symptom: Product Event Extraction Failed

Likely tasks:

- `generate_product_events`
- `extract_product_events`

Checks:

- confirm generated files exist under `data/product_events`;
- confirm extractor can read NDJSON files;
- confirm output raw path exists under `raw/events/product_events`.

## RAW Loading Incident Response

### Symptom: API or Event Records Missing in `raw.json_records`

Likely tasks:

- `load_api_raw_json`
- `load_product_events_raw_json`

Check row counts:

`docker exec revopspulse-postgres psql -U revopspulse -d revopspulse -c "select source_system, source_entity, count(*) from raw.json_records group by 1, 2 order by 1, 2;"`

Common causes:

| Cause | Fix |
|---|---|
| Raw file path missing | Re-run extraction task |
| JSON parse issue | Inspect failing JSONL file |
| Duplicate record hashes | Confirm deduplication is expected |
| Missing metadata | Check extractor output schema |

## dbt Incident Response

### Symptom: dbt Build Failed

Run dbt manually:

`docker run --rm --network revopspulse-modern-data-stack_default -v "$PWD/dbt:/usr/app" -w /usr/app -e DEBIAN_FRONTEND=noninteractive -e PIP_ROOT_USER_ACTION=ignore -e POSTGRES_HOST=postgres -e POSTGRES_PORT=5432 -e POSTGRES_DB=revopspulse -e POSTGRES_USER=revopspulse -e POSTGRES_PASSWORD=revopspulse python:3.12-slim sh -c "set -e && apt-get update >/dev/null && apt-get install -y --no-install-recommends git >/dev/null && pip install --no-cache-dir dbt-postgres==1.9.0 >/dev/null && dbt build --profiles-dir /usr/app"`

Interpretation:

| Result | Meaning |
|---|---|
| `ERROR=0` | Build passed |
| `WARN>0` | Build passed with warnings |
| `ERROR>0` | Build failed and must be fixed |

Known accepted warnings:

- `valid_subscription_period`
- `amount_non_negative` on `fact_payments.net_paid_amount`
- `refund_not_greater_than_payment`

These are intentional synthetic anomalies.

### Symptom: Snapshot Failed

Likely task:

`dbt_snapshot`

Checks:

- confirm `subscription_snapshot` SQL exists;
- confirm source subscriptions table exists;
- confirm `updated_at` exists in source subscriptions;
- run `dbt snapshot` manually.

### Symptom: Incremental Model Failed

Likely model:

`fact_product_events`

Checks:

- confirm `event_id` is unique;
- confirm `event_timestamp` is not null;
- confirm staging event model exists;
- run `dbt build --select fact_product_events`.

## Data Quality Incident Response

### Expected Quality Warnings

The project intentionally includes synthetic anomalies.

Expected warnings:

| Test | Expected Failed Records |
|---|---:|
| `valid_subscription_period` | 1 |
| `amount_non_negative` | 1 |
| `refund_not_greater_than_payment` | 1 |

These should appear in dbt output as warnings and in `mart_data_quality_summary`.

### Unexpected Quality Failure

If a new data quality failure appears:

1. Identify the failing test.
2. Query the failing model.
3. Determine if the failure is expected synthetic data or a modeling bug.
4. If expected, document it and configure severity appropriately.
5. If unexpected, fix the source generator, extractor or dbt model.
6. Re-run the narrow dbt test.
7. Re-run full `dbt build`.

## Final Mart Validation

After any fix, validate final marts:

`docker exec revopspulse-postgres psql -U revopspulse -d revopspulse -c "select 'mart_revenue_monthly' as model_name, count(*) as row_count from analytics.mart_revenue_monthly union all select 'mart_product_usage_daily', count(*) from analytics.mart_product_usage_daily union all select 'mart_marketing_roi_monthly', count(*) from analytics.mart_marketing_roi_monthly union all select 'mart_sales_commissions_monthly', count(*) from analytics.mart_sales_commissions_monthly union all select 'mart_data_quality_summary', count(*) from analytics.mart_data_quality_summary union all select 'subscription_snapshot', count(*) from snapshots.subscription_snapshot order by model_name;"`

Expected latest counts:

| Model | Rows |
|---|---:|
| `mart_data_quality_summary` | 4 |
| `mart_marketing_roi_monthly` | 33 |
| `mart_product_usage_daily` | 89 |
| `mart_revenue_monthly` | 6 |
| `mart_sales_commissions_monthly` | 18 |
| `subscription_snapshot` | 15 |

## Rollback and Recovery

### Safe Rollback

If a code change breaks the pipeline before commit:

`git checkout -- <file>`

Use this only when you intentionally want to discard local changes.

### Rebuild dbt Objects

Run full dbt build manually or through Airflow.

### Restart Services

Restart a specific service:

`docker compose restart <service_name>`

Restart all services:

`docker compose restart`

### Full Local Reset

Avoid full reset unless intentionally starting over.

Destructive command:

`docker compose down -v`

This deletes local Postgres volumes and removes databases.

Use only when you are prepared to recreate source data, Airflow metadata and analytics models.

## Communication Template

For portfolio documentation, an incident summary should include:

| Field | Description |
|---|---|
| Incident | What failed |
| Severity | SEV level |
| Impact | Which data products were affected |
| Detection | How it was detected |
| Root cause | Why it happened |
| Fix | What was changed |
| Validation | Evidence that the fix worked |
| Prevention | How similar issues will be avoided |

## Post-Incident Checklist

After resolving an incident:

- commit the fix;
- update docs if behavior changed;
- re-run narrow validation;
- re-run full dbt build;
- re-run Airflow DAG if orchestration was affected;
- validate final marts;
- ensure Git working tree is clean.

## Known Non-Blocking Warnings

Airflow containers may show pip dependency resolver warnings related to protobuf.

The latest validated end-to-end DAG run completed successfully despite these warnings.

This should be cleaned up later with a custom Airflow image, but it is not blocking the MVP.

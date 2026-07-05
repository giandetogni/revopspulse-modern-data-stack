# RevOpsPulse — Modern Data Stack for SaaS Revenue, Retention & Incentive Analytics

RevOpsPulse is an end-to-end modern data stack project for SaaS Revenue Operations analytics.

It ingests synthetic CRM, billing, product usage and sales incentive data, orchestrates ELT with Airflow, loads raw API and event records, transforms trusted analytics models with dbt, and delivers revenue, churn, product adoption, marketing ROI and commission metrics.

The project is designed as a portfolio-grade data engineering and analytics engineering case study for international remote roles.

## Executive Summary

RevOpsPulse demonstrates:

- Python ingestion from PostgreSQL, a mock paginated CRM API and NDJSON product events.
- Airflow orchestration with explicit task dependencies instead of one large script.
- RAW preservation with extraction metadata, batch IDs and record hashes.
- dbt staging, intermediate and marts layers.
- dbt tests, custom business rule tests, source definitions and snapshots.
- Incremental dbt modeling for product events.
- SaaS metrics: MRR, ARR, churn, retention, product adoption, marketing ROI and sales commissions.
- CI/CD with Python quality checks and dbt build validation.
- Technical documentation, runbook, incident response, cost estimate and trade-off notes.

## Problem

Revenue Operations teams need reliable answers to questions such as:

- How much recurring revenue do we have?
- Which customers are active, inactive or churning?
- Which campaigns generate efficient pipeline?
- Are sales commissions paid only on eligible revenue?
- Which product features correlate with activation and retention?

In real companies, these answers often require joining operational databases, CRM APIs, billing data, product events and sales target data. Without a governed analytics pipeline, metrics become inconsistent, stale or impossible to audit.

## Solution

RevOpsPulse simulates a realistic SaaS data platform.

The pipeline:

1. Generates deterministic synthetic SaaS source data.
2. Loads OLTP-style tables into PostgreSQL.
3. Extracts PostgreSQL tables to RAW CSV files.
4. Serves CRM and marketing data through a mock API with pagination and `updated_since` incremental filtering.
5. Extracts API data to RAW JSONL files with retries and metadata.
6. Generates product event NDJSON files.
7. Extracts product events into RAW JSONL files.
8. Loads API and event RAW records into a warehouse-style `raw.json_records` table.
9. Runs dbt staging, intermediate, marts, custom tests, snapshot and incremental models.
10. Produces final analytics-ready marts and a data quality summary.

## Architecture

```text
PostgreSQL OLTP source
  accounts, customers, plans, subscriptions, invoices,
  payments, refunds, sales_reps, sales_targets

Mock CRM / Marketing API
  leads, campaigns, opportunities, marketing_spend

Product Event NDJSON files
  login, account_created, invite_user, create_project,
  use_core_feature, export_report, upgrade_prompt_viewed,
  billing_page_viewed, cancellation_started

        |
        v

Python extractors
  src/ingestion/postgres_extractor.py
  src/ingestion/api_extractor.py
  src/ingestion/events_extractor.py
  src/ingestion/raw_json_loader.py

        |
        v

RAW storage
  raw/postgres/*
  raw/api/*
  raw/events/*

        |
        v

Airflow DAG
  dags/revopspulse_daily_pipeline.py

        |
        v

PostgreSQL local warehouse
  source schema
  raw schema
  analytics schema
  snapshots schema

        |
        v

dbt
  staging
  intermediate
  marts
  snapshots
  tests

        |
        v

Analytics marts
  revenue
  product usage
  marketing ROI
  sales commissions
  data quality summary
```

## Current Implementation Status

This repository is runnable locally with Docker Compose and PostgreSQL.

Snowflake or BigQuery are documented as production warehouse options and future adapter targets. The current implementation intentionally uses PostgreSQL as the local warehouse so the project is cheap, reproducible and CI-friendly.

## Stack

| Layer | Tooling |
|---|---|
| Language | Python, SQL |
| Source database | PostgreSQL 16 |
| Orchestration | Apache Airflow 3 |
| Transformation | dbt + dbt-postgres |
| Local runtime | Docker Compose |
| Testing | pytest, dbt tests, custom dbt tests |
| CI/CD | GitHub Actions |
| Documentation | Markdown docs + dbt project structure |

## Data Sources

### PostgreSQL OLTP

Synthetic transactional source tables:

- `accounts`
- `customers`
- `plans`
- `subscriptions`
- `invoices`
- `payments`
- `refunds`
- `sales_reps`
- `sales_targets`

### Mock CRM and Marketing API

The API is implemented in `src/api_mock/mock_crm_api.py`.

Endpoints:

- `/health`
- `/leads`
- `/campaigns`
- `/opportunities`
- `/marketing_spend`

Implemented API behaviors:

- pagination with `page` and `page_size`;
- incremental filtering with `updated_since`;
- deterministic synthetic records;
- extraction with retry handling and RAW metadata.

### Product Events

Generated event types:

- `login`
- `account_created`
- `invite_user`
- `create_project`
- `use_core_feature`
- `export_report`
- `upgrade_prompt_viewed`
- `billing_page_viewed`
- `cancellation_started`

Product events are generated as NDJSON files and then extracted into RAW JSONL records.

## Airflow DAG

Main DAG:

```text
revopspulse_daily_pipeline
```

Tasks:

```text
extract_postgres_sources
extract_api_sources
load_api_raw_json
generate_product_events
extract_product_events
load_product_events_raw_json
dbt_snapshot
dbt_build
```

The DAG is intentionally split into multiple tasks to make orchestration, dependencies and failure boundaries visible.

## dbt Layers

### Staging

Staging models standardize source records with light cleanup and casting.

Examples:

- `stg_postgres__accounts`
- `stg_postgres__subscriptions`
- `stg_postgres__payments`
- `stg_api__opportunities`
- `stg_api__marketing_spend`
- `stg_events__product_events`

### Intermediate

Intermediate models hold reusable business logic.

Implemented examples:

- `int_payments_enriched`
- `int_opportunities_enriched`
- `int_product_usage_account_daily`

### Marts

Implemented marts:

- `dim_accounts`
- `dim_customers`
- `dim_sales_reps`
- `fact_payments`
- `fact_opportunities`
- `fact_product_events`
- `mart_revenue_monthly`
- `mart_product_usage_daily`
- `mart_marketing_roi_monthly`
- `mart_sales_commissions_monthly`
- `mart_data_quality_summary`

## Incremental Model

`fact_product_events` is materialized incrementally.

It uses `event_id` as the unique key and only processes new events based on the maximum loaded event timestamp.

## Snapshot / SCD Type 2

`subscription_snapshot` tracks subscription history using dbt snapshots.

Snapshot strategy:

- unique key: `subscription_id`
- strategy: `timestamp`
- updated timestamp: `updated_at`

This demonstrates SCD Type 2 tracking for subscription lifecycle changes.

## Core Metrics

### Revenue

- MRR
- ARR
- gross revenue
- net revenue
- refund amount
- payment failure rate
- refund rate
- churn rate
- logo retention rate

### Product

- total events
- active accounts
- inactive accounts
- active users
- activation rate
- core feature adoption rate
- report export adoption rate
- cancellation intent rate

### Marketing

- marketing spend
- leads
- opportunities
- closed-won opportunities
- closed-won revenue
- cost per lead
- CAC
- lead-to-opportunity conversion rate
- marketing ROI

### Sales Commissions

Commission rules implemented:

- closed-won opportunity plus paid invoice qualifies for commission;
- base commission is 5% of eligible net paid revenue;
- reps at or above 100% quota receive 8% commission on above-quota revenue;
- refunds or cancellations within 30 days create clawbacks;
- unpaid invoices, failed payments and non-closed-won opportunities do not generate commission.

Metrics:

- quota attainment
- commissionable revenue
- base commission
- accelerator commission
- clawback amount
- commission payout
- commission accuracy rate

## Data Quality

The project includes intentional synthetic data quality issues so tests and quality reporting are meaningful.

Examples:

- duplicate customer emails;
- negative invoice amounts;
- invalid subscription periods;
- payments missing invoice IDs;
- refunds greater than payment amount.

Implemented dbt test coverage includes generic and custom tests such as:

- `unique`
- `not_null`
- `relationships`
- `accepted_values`
- `amount_non_negative`
- `valid_subscription_period`
- `refund_not_greater_than_payment`
- `event_timestamp_not_future`

The final data quality mart is:

```text
mart_data_quality_summary
```

It includes:

- `run_date`
- `source_name`
- `model_name`
- `test_name`
- `severity`
- `status`
- `failed_records`
- `total_records`
- `failure_rate`
- `business_impact`
- `created_at`

## CI/CD

GitHub Actions workflows:

```text
.github/workflows/ci.yml
.github/workflows/dbt-ci.yml
```

Python CI validates:

- `ruff check src dags tests`
- `black --check src dags tests`
- `pytest -q tests/unit`
- `docker compose config`

dbt CI validates:

- PostgreSQL service startup
- source schema and seed load
- RAW API and product event generation
- RAW JSON loading
- `dbt debug`
- `dbt deps`
- `dbt parse`
- `dbt compile`
- `dbt snapshot`
- `dbt build`

## Documentation

Additional documentation:

- `docs/data_dictionary.md`
- `docs/data_model.md`
- `docs/metric_definitions.md`
- `docs/runbook.md`
- `docs/incident_response.md`
- `docs/assumptions.md`
- `docs/cost_estimate.md`
- `docs/tradeoffs.md`
- `docs/project_scope.md`

## How to Run Locally

### 1. Start Docker Desktop

Docker must be running before starting the project.

### 2. Start services

```bash
docker compose up -d
```

### 3. Check containers

```bash
docker compose ps
```

### 4. Trigger the Airflow DAG

Airflow is exposed locally on port `8080`.

The main DAG is:

```text
revopspulse_daily_pipeline
```

You can also trigger it from the Airflow CLI inside the scheduler container:

```bash
docker exec revopspulse-airflow-scheduler airflow dags trigger revopspulse_daily_pipeline
```

### 5. Run dbt manually

```bash
cp dbt/profiles.yml.example dbt/profiles.yml

dbt debug --project-dir dbt --profiles-dir dbt
dbt deps --project-dir dbt --profiles-dir dbt
dbt snapshot --project-dir dbt --profiles-dir dbt
dbt build --project-dir dbt --profiles-dir dbt
```

### 6. Run Python checks

```bash
source .venv/bin/activate

ruff check src dags tests
black --check src dags tests
pytest -q tests/unit
```

## Reproducibility Notes

The synthetic data generators are deterministic and seed-driven.

Local generated files are intentionally ignored by Git:

- `raw/`
- `data/`
- `logs/`
- `dbt/target/`
- `dbt/dbt_packages/`
- `.venv/`

The repository tracks source code, SQL, dbt models, tests, docs and CI definitions, not generated runtime artifacts.

## Security

This project uses only synthetic data.

Security practices:

- no real employer data;
- no customer data;
- no banking data;
- no committed `.env`;
- no committed real credentials;
- `.env.example` contains placeholders only;
- Airflow local secrets are parameterized through environment variables;
- dbt profile is provided as `profiles.yml.example`.

## Cost

The MVP is designed to run locally using Docker Compose.

Expected local cost: zero cloud spend.

Production deployment trade-offs for Snowflake or BigQuery are documented in `docs/cost_estimate.md` and `docs/tradeoffs.md`.

## Trade-offs

Intentional MVP trade-offs:

- PostgreSQL is used as the local warehouse to keep the project reproducible.
- Snowflake or BigQuery are not required for local execution.
- Kafka, Spark, Kubernetes and ML are excluded from the MVP.
- The dashboard layer is intentionally lightweight and secondary to pipeline, dbt models, tests and documentation.
- The project favors clear employability signal over unnecessary platform complexity.

## Limitations

Current limitations:

- data is synthetic;
- product usage and revenue recognition are simplified for portfolio scope;
- MRR is modeled for demonstration and not a full billing-system replacement;
- local PostgreSQL simulates warehouse behavior;
- dashboard artifacts are not the primary focus yet;
- CI validates the project with PostgreSQL, not Snowflake or BigQuery.

## Future Work

High-ROI future improvements:

- add lightweight dashboard screenshots;
- publish dbt docs artifacts;
- add more dimensional model diagrams;
- add Snowflake or BigQuery adapter path;
- add additional revenue retention metrics such as GRR, NRR and cohort retention;
- add a small `revopspulse_backfill` Airflow DAG;
- add richer dashboard examples using Evidence, Streamlit or Metabase.

## Project Narrative

RevOpsPulse demonstrates the ability to design and implement a modern analytics platform for SaaS Revenue Operations.

It proves practical skills in Python ingestion, Airflow orchestration, dbt modeling, data quality, incremental loading, SCD Type 2 snapshots, SaaS metrics, CI/CD and technical documentation without relying on over-engineered tools before the MVP is complete.

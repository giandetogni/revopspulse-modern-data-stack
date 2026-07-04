# RevOpsPulse — Modern Data Stack for SaaS Revenue, Retention & Incentive Analytics

RevOpsPulse is an end-to-end modern data stack project that ingests CRM, billing, product usage and sales incentive data, orchestrates incremental ELT pipelines with Airflow, transforms trusted analytics models with dbt, and delivers revenue, churn, retention and commission metrics in a cloud data warehouse.

## Problem

SaaS and fintech Revenue Operations teams need trusted answers about recurring revenue, churn, customer retention, marketing efficiency and sales incentives.

In practice, these metrics are usually spread across operational databases, CRM systems, billing data, product events and sales target files. Without a reliable data pipeline, teams risk making decisions based on stale, inconsistent or poorly modeled data.

## Solution

RevOpsPulse simulates a realistic Revenue Operations data platform.

The project ingests synthetic SaaS data from:

- PostgreSQL transactional tables
- Mock CRM and marketing API endpoints
- JSON or NDJSON product event files

The pipeline preserves raw records, loads them into a cloud warehouse, transforms them with dbt into staging, intermediate and mart models, applies data quality checks, and exposes trusted metrics for revenue, retention, product usage, marketing and sales commissions.

## Target Stack

- Python
- PostgreSQL
- Apache Airflow
- dbt
- Snowflake as the preferred warehouse
- BigQuery as fallback
- Docker Compose
- GitHub Actions
- SQL
- Streamlit, Evidence or Metabase for lightweight dashboarding

## Architecture Draft

    PostgreSQL OLTP Source
    Mock CRM / Marketing API
    Product Event JSON Files
            |
            v
    Python Extractors
            |
            v
    Raw Storage
            |
            v
    Airflow DAG
            |
            v
    Snowflake / BigQuery RAW schema
            |
            v
    dbt staging
            |
            v
    dbt intermediate
            |
            v
    dbt marts
            |
            v
    Dashboard / BI outputs

## Data Sources

### PostgreSQL

Core transactional source with synthetic SaaS tables:

- customers
- accounts
- plans
- subscriptions
- invoices
- payments
- refunds
- sales_reps
- sales_targets

### Mock API

Simulated CRM and marketing endpoints:

- crm_opportunities
- leads
- marketing_campaigns

The API ingestion will demonstrate pagination, retry logic, logging and incremental extraction by updated_at.

### Product Events

JSON or NDJSON product usage events:

- account_created
- login
- invite_user
- create_project
- use_core_feature
- export_report
- upgrade_prompt_viewed
- billing_page_viewed
- cancellation_started

## Pipeline Design

The MVP pipeline will include:

1. Generate synthetic SaaS data.
2. Load transactional data into PostgreSQL.
3. Extract Postgres, API and event data with Python.
4. Add extraction metadata such as batch_id, extracted_at, load_date, source_system and record_hash.
5. Store raw files.
6. Load raw data into the warehouse.
7. Run dbt sources, staging, intermediate and mart models.
8. Run dbt tests and source freshness checks.
9. Build final revenue, retention, marketing, product and commission metrics.
10. Publish a data quality summary and dashboard outputs.

## dbt Modeling Plan

The dbt project will follow a layered modeling structure:

- staging: source-aligned cleanup, casting and naming standardization
- intermediate: reusable business logic
- marts: analytics-ready facts, dimensions and business metrics

Required dbt features:

- sources
- source freshness
- staging models
- intermediate models
- marts
- generic tests
- custom tests
- at least one incremental model
- at least one snapshot / SCD Type 2 model
- dbt documentation

## Key Metrics

Revenue:

- MRR
- ARR
- gross revenue
- net revenue
- payment failure rate
- refund rate

Retention:

- churn rate
- logo retention
- gross revenue retention
- net revenue retention
- cohort retention
- expansion and contraction revenue

Product:

- activation rate
- daily active accounts
- core feature adoption
- inactive accounts

Marketing:

- CAC
- conversion rate
- marketing ROI
- cost per lead

Sales incentives:

- quota attainment
- commissionable revenue
- commission payout
- clawback amount
- commission accuracy rate

## Data Quality

The project will include intentional synthetic data quality issues such as duplicate emails, orphan payments, invalid subscription periods, negative invoice amounts, future product events and refunds greater than payments.

These issues will be surfaced through dbt tests, source freshness checks and a final mart_data_quality_summary model.

## MVP Scope

The MVP must prove:

- Airflow orchestration
- Python ingestion
- PostgreSQL source extraction
- API extraction with pagination
- product event ingestion
- raw data preservation
- warehouse loading
- dbt modeling
- dbt tests
- source freshness
- incremental models
- snapshots / SCD Type 2
- revenue, retention and commission metrics
- CI/CD
- documentation
- reproducibility

## Out of Scope Before MVP

The following are intentionally excluded before the core pipeline works:

- Kafka
- Spark
- Kubernetes
- machine learning
- real-time streaming
- complex frontend
- data mesh
- multi-cloud architecture
- production-grade observability

## Security

This project uses only synthetic data.

No real employer, customer or banking data should be used. Secrets must be provided through environment variables and never committed to the repository.

## Current Status

Project foundation in progress.

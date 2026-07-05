# RevOpsPulse Demo Script

## 30-second overview

RevOpsPulse is a modern data stack portfolio project for SaaS revenue, retention, product usage, marketing ROI and sales incentive analytics.

It simulates a Revenue Operations data platform that ingests data from PostgreSQL, a mock CRM/marketing API and product event files, orchestrates the pipeline with Airflow, transforms the warehouse with dbt and exposes analytics-ready marts with revenue, churn, retention, commission and data quality metrics.

## 1. Business problem

SaaS and fintech teams often have revenue data spread across multiple systems: billing databases, CRM tools, marketing platforms, product events and sales incentive spreadsheets.

The problem is not only visualizing metrics. The real challenge is building a reproducible pipeline that ingests, validates, models and documents trusted metrics such as MRR, ARR, churn, payment failure rate, marketing ROI, quota attainment and commission payout.

## 2. Architecture

The project uses three source types:

- PostgreSQL transactional data for customers, accounts, subscriptions, invoices, payments, refunds and sales targets.
- A mock CRM/marketing API for leads, campaigns, opportunities and marketing spend.
- Product usage events generated as NDJSON files.

Python extractors preserve raw records with metadata such as source system, batch ID, extracted timestamp, load date, raw file path and record hash.

Airflow orchestrates extraction, raw loading, dbt snapshots and dbt builds.

dbt organizes the warehouse into staging, intermediate and mart layers.

## 3. Airflow orchestration

The main DAG is `revopspulse_daily_pipeline`.

It separates extraction and transformation steps instead of hiding the full process inside one task.

The pipeline includes:

- PostgreSQL extraction
- API extraction
- Product event generation and extraction
- Raw JSON loading
- dbt snapshot
- dbt build

Execution evidence is included in `docs/screenshots/airflow_dag.png`.

## 4. dbt modeling

The dbt project includes:

- Staging models for PostgreSQL, API and event sources.
- Intermediate models for payments, opportunities and product usage.
- Dimensional marts such as accounts, customers, sales reps, payments, opportunities and product events.
- Business marts for revenue, product usage, marketing ROI, sales commissions and data quality.

The project includes an incremental model for product events and a subscription snapshot to demonstrate SCD Type 2 logic.

## 5. Metrics

The final marts calculate:

- MRR and ARR
- Gross and net revenue
- Payment failure rate
- Refund rate
- Churn rate
- Logo retention
- Product activation rate
- Core feature adoption
- Marketing ROI
- Cost per lead
- Quota attainment
- Commissionable revenue
- Commission payout
- Clawback amount

A lightweight metrics snapshot is available in `dashboard/metrics_snapshot.md`.

## 6. Data quality

The project intentionally generates some data quality issues to demonstrate validation.

Examples include:

- Negative payment amount
- Refund greater than payment
- Invalid subscription period
- Future event timestamp validation

The final `mart_data_quality_summary` table turns these checks into a business-facing quality report with failed records, failure rate and business impact.

## 7. CI/CD and reproducibility

The repository has GitHub Actions for:

- Python linting
- Black formatting check
- Pytest unit tests
- dbt parse, compile, snapshot and build

The latest evidence screenshot is available in `docs/screenshots/github_actions.png`.

The project uses synthetic data only, avoids committed secrets and includes `.env.example` and `profiles.yml.example`.

## 8. Main trade-offs

This MVP uses PostgreSQL as the local warehouse to keep the project reproducible and cost-controlled.

In production, I would consider Snowflake or BigQuery, managed Airflow, stronger observability, real secrets management and more robust incremental watermarking.

I intentionally avoided Kafka, Spark, Kubernetes and ML because the main goal was to prove modern analytics engineering with Airflow, dbt, data quality and business metrics.

## 9. Closing

RevOpsPulse complements my HarborWatch AWS lakehouse project.

Together, they show that I can build both cloud lakehouse pipelines and modern warehouse-based analytics engineering projects with orchestration, modeling, tests, documentation and business-facing metrics.

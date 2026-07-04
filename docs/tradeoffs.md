# Trade-offs

This document explains the main technical trade-offs made in RevOpsPulse. The goal is to keep the MVP focused, reproducible and valuable as an analytics engineering portfolio project.

## Guiding Principle

The project prioritizes employability signal over infrastructure complexity.

The intended signal is:

- Airflow orchestration;
- Python ingestion;
- API pagination and incremental extraction;
- RAW to staging to intermediate to marts;
- dbt tests;
- dbt snapshots;
- incremental models;
- dimensional modeling;
- SaaS revenue and retention metrics;
- sales commission logic;
- documentation and reproducibility.

## Local Docker Compose vs Managed Cloud

### Decision

Use Docker Compose locally for the MVP.

### Why

Docker Compose makes the project reproducible without requiring paid cloud infrastructure or real credentials.

It also allows reviewers to inspect the full stack locally.

### Trade-off

This is not production-grade infrastructure.

A production deployment would likely use:

- managed Airflow or a scheduler service;
- managed warehouse such as Snowflake or BigQuery;
- external object storage;
- managed secrets;
- monitoring and alerting;
- CI/CD deployment workflows.

### Why This Is Acceptable

The MVP needs to prove data engineering and analytics engineering patterns, not cloud operations complexity.

## PostgreSQL as Local Warehouse vs Snowflake or BigQuery

### Decision

Use PostgreSQL locally as the source database, Airflow metadata database and analytics database for the MVP.

### Why

PostgreSQL is easy to run locally and supports enough SQL features for the project:

- schemas;
- views;
- incremental tables;
- snapshots;
- joins;
- window functions;
- date operations.

### Trade-off

PostgreSQL does not demonstrate full cloud warehouse capabilities such as elastic scaling, native external stages or warehouse separation.

### Future Upgrade

The dbt project can be adapted to Snowflake or BigQuery after the MVP is stable.

This should happen only after the local pipeline, dbt models, tests and documentation are complete.

## Airflow vs Simple Cron or Makefile

### Decision

Use Airflow for orchestration.

### Why

Airflow is a target skill for the project and gives stronger employability signal than a simple script runner.

The DAG demonstrates:

- task dependencies;
- retries;
- pipeline stages;
- extraction;
- raw loading;
- dbt snapshot;
- dbt build.

### Trade-off

Airflow adds local complexity, especially with Docker and metadata setup.

### Why This Is Acceptable

Airflow is one of the core technologies this project is designed to prove.

## Mock API vs Real Third-Party API

### Decision

Use a mock CRM and marketing API.

### Why

The project needs deterministic, reproducible data without using real customer or company information.

The mock API still demonstrates important ingestion patterns:

- endpoints;
- pagination;
- incremental extraction by `updated_since`;
- retry logic;
- logging;
- JSON extraction.

### Trade-off

The API does not represent all real-world API problems such as OAuth, rate limits, schema drift and partial outages.

### Future Upgrade

Add simulated API failures, rate-limit responses and schema drift tests after the MVP.

## Synthetic Data vs Real Data

### Decision

Use synthetic data only.

### Why

The project must be safe to publish publicly.

No real customer, employer, banking, financial institution or internal company data should be used.

### Trade-off

Synthetic data may not capture every real-world business edge case.

### Why This Is Acceptable

The purpose is to prove pipeline design, modeling, testing and documentation patterns.

## dbt Staging Discipline

### Decision

Keep staging models lightweight.

### Why

Staging models should standardize source data without embedding heavy business rules.

Business logic belongs in intermediate and marts layers.

### Trade-off

This creates more models than putting all logic in a few large SQL files.

### Why This Is Acceptable

Layered dbt modeling is easier to review, test and maintain.

## Intermediate Layer vs Direct Mart Logic

### Decision

Use intermediate models for reusable logic.

### Why

Intermediate models reduce duplication and make business logic easier to validate.

Examples:

- `int_payments_enriched`;
- `int_opportunities_enriched`;
- `int_product_usage_account_daily`.

### Trade-off

The project has more dbt nodes.

### Why This Is Acceptable

This structure better reflects professional analytics engineering practice.

## Views vs Tables

### Decision

Most marts are materialized as views. `fact_product_events` is materialized incrementally as a table.

### Why

Views keep the local MVP simple and avoid unnecessary storage management.

The event fact is incremental to demonstrate append-oriented event processing.

### Trade-off

Views are recomputed at query time and may not be optimal at larger scale.

### Future Upgrade

Materialize high-traffic marts as tables in a cloud warehouse.

## Incremental Model Scope

### Decision

Use `fact_product_events` as the main incremental model.

### Why

Product events are naturally append-oriented and keyed by `event_id`.

The model demonstrates incremental processing with a clear unique key and timestamp filter.

### Trade-off

The MVP does not implement complex late-arriving event reconciliation.

### Future Upgrade

Add lookback windows and deduplication strategies for late-arriving events.

## Snapshot Scope

### Decision

Use `subscription_snapshot` as the SCD Type 2 example.

### Why

Subscriptions are a natural entity for lifecycle changes and historical analysis.

The snapshot uses:

- `subscription_id` as unique key;
- timestamp strategy;
- `updated_at` as change marker.

### Trade-off

The current revenue mart does not yet use the snapshot for month-accurate MRR.

### Future Upgrade

Use snapshot history to calculate historical MRR, GRR and NRR.

## Revenue Modeling Simplicity

### Decision

MRR is calculated from current subscription status and plan price.

### Why

This keeps the MVP understandable and avoids overbuilding historical subscription logic before the rest of the stack is complete.

### Trade-off

Historical MRR can be inaccurate if subscription status or plan price changes over time.

### Future Upgrade

Build a subscription history spine using `subscription_snapshot`.

## Marketing Attribution Simplicity

### Decision

Use campaign/month attribution.

### Why

It demonstrates marketing ROI and funnel metrics without building a complex attribution engine.

### Trade-off

Leads and opportunities can occur in different months, so monthly conversion rates can exceed 1.0 in synthetic data.

### Future Upgrade

Add attribution windows and first-touch or last-touch campaign logic.

## Commission Logic Simplicity

### Decision

Use simplified account-level opportunity attribution for sales commissions.

### Why

It proves core incentive analytics rules:

- closed-won plus paid invoice;
- 5% base commission;
- 8% accelerator above quota;
- 30-day refund clawback;
- failed or unpaid invoices excluded.

### Trade-off

It does not support split credit, ramp quota, territory rules or multiple compensation plans.

### Future Upgrade

Add compensation plan versioning and payout audit tables.

## Data Quality Warnings vs Failures

### Decision

Known synthetic anomalies are configured as warnings where appropriate.

### Why

The project intentionally includes data quality issues to demonstrate tests and `mart_data_quality_summary`.

### Trade-off

Warnings allow the pipeline to complete even with known anomalies.

### Why This Is Acceptable

The warnings are intentional, documented and surfaced in a data quality mart.

## Not Using Spark

### Decision

Do not use Spark in the MVP.

### Why

The data volume is small and Spark would add unnecessary complexity.

### Trade-off

The project does not demonstrate distributed processing.

### Why This Is Acceptable

The target signal is modern ELT and analytics engineering, not big data processing.

## Not Using Kafka

### Decision

Do not use Kafka in the MVP.

### Why

The project does not need streaming infrastructure to demonstrate the target skills.

### Trade-off

The project does not demonstrate real-time ingestion.

### Why This Is Acceptable

Batch orchestration with Airflow is more relevant to the MVP.

## Not Using Kubernetes

### Decision

Do not use Kubernetes in the MVP.

### Why

Kubernetes would add infrastructure scope without improving the core analytics engineering signal.

### Trade-off

The local stack is not production-orchestrated.

### Why This Is Acceptable

Docker Compose is enough for local reproducibility.

## Not Using Machine Learning

### Decision

Do not add machine learning before the MVP is complete.

### Why

The project is about data engineering and analytics engineering, not predictive modeling.

### Trade-off

No churn prediction or lead scoring is included.

### Why This Is Acceptable

Reliable pipelines, tests, data models and business metrics are higher ROI for the portfolio goal.

## Summary

The MVP intentionally favors:

- clear pipelines over complex infrastructure;
- dbt modeling over dashboard polish;
- reproducibility over cloud cost;
- business metrics over technical vanity;
- documented limitations over hidden assumptions.

These trade-offs keep the project focused and defensible.

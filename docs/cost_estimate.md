# Cost Estimate

This document explains the expected cost profile for RevOpsPulse as a local MVP and as a potential cloud deployment.

## Summary

The current MVP is designed to run locally with Docker Compose.

Current MVP cost:

| Component | Cost |
|---|---:|
| Docker Compose | $0 |
| Local PostgreSQL | $0 |
| Local Airflow | $0 |
| Local mock API | $0 |
| Local dbt Core | $0 |
| Local synthetic data | $0 |
| Total local runtime cost | $0 |

The only cost is the developer machine and local electricity usage.

## Why the MVP Avoids Cloud Costs

The MVP intentionally avoids real cloud infrastructure because the project goal is to prove:

- ingestion patterns;
- Airflow orchestration;
- dbt modeling;
- incremental loading;
- snapshots;
- business metrics;
- data quality;
- documentation;
- reproducibility.

Using cloud infrastructure before the MVP is complete would increase setup complexity without improving the core analytics engineering signal.

## Local Runtime Components

| Component | Runtime Mode | Cost Impact |
|---|---|---|
| PostgreSQL | Docker container | No external cost |
| Airflow | Docker containers | No external cost |
| Mock CRM API | Docker container | No external cost |
| dbt Core | Docker or local Python | No external cost |
| Raw files | Local filesystem | No external cost |
| Synthetic data | Generated locally | No external cost |

## Estimated Cloud Architecture

A production-like cloud version could use:

| Layer | Example Service |
|---|---|
| Object storage | AWS S3, GCS or Azure Blob Storage |
| Warehouse | Snowflake or BigQuery |
| Orchestration | Managed Airflow or self-hosted Airflow |
| Secrets | Cloud secrets manager |
| Monitoring | Cloud logs and alerts |
| BI | Metabase, Evidence, Streamlit or warehouse-native dashboards |

## Small Cloud MVP Estimate

A minimal cloud MVP could remain inexpensive if usage is tightly controlled.

Estimated monthly range:

| Component | Estimated Monthly Cost |
|---|---:|
| Object storage for synthetic raw data | $0 - $5 |
| Cloud warehouse development usage | $0 - $30 |
| Managed scheduler or small Airflow host | $0 - $50 |
| Logs and monitoring | $0 - $10 |
| Dashboard hosting | $0 - $20 |
| Total estimated monthly cost | $0 - $115 |

This estimate assumes very small synthetic data volumes and limited development runs.

## Cost Drivers

The main cost drivers in a cloud deployment would be:

| Driver | Why It Matters |
|---|---|
| Warehouse compute | dbt builds and dashboard queries consume warehouse resources |
| Storage | Raw files, snapshots and materialized marts accumulate over time |
| Airflow runtime | Managed Airflow can be expensive even for small DAGs |
| Query frequency | Frequent dashboard refreshes increase warehouse usage |
| Log retention | Long retention periods increase observability cost |
| CI/CD runs | Repeated dbt builds in CI can increase warehouse usage |

## Warehouse Cost Controls

Recommended controls for Snowflake or BigQuery:

| Control | Purpose |
|---|---|
| Use small warehouse size | Avoid overprovisioned compute |
| Auto-suspend warehouse | Stop compute when idle |
| Limit dashboard refreshes | Avoid unnecessary query costs |
| Use incremental models | Reduce full rebuild cost |
| Materialize only high-value marts | Avoid unnecessary tables |
| Keep dev and prod separate | Prevent accidental expensive runs |
| Add query limits where available | Reduce runaway query risk |

## Airflow Cost Controls

Airflow can become a cost driver if deployed as a managed service.

Recommended controls:

| Control | Purpose |
|---|---|
| Prefer local Airflow for MVP | Avoid unnecessary managed service cost |
| Use managed Airflow only when needed | Avoid paying for idle infrastructure |
| Keep DAG frequency low | Daily schedule is enough for this MVP |
| Avoid unnecessary backfills | Backfills can multiply compute usage |
| Monitor task duration | Long tasks often point to inefficient logic |

## Storage Cost Controls

Recommended controls:

| Control | Purpose |
|---|---|
| Partition raw files by load date | Easier cleanup and lifecycle policies |
| Compress large raw files | Lower storage cost |
| Apply retention policy | Avoid unlimited raw data growth |
| Keep synthetic data small | Maintain local reproducibility |
| Avoid committing generated raw data | Prevent repository bloat |

## CI/CD Cost Controls

For a public portfolio project, CI should avoid requiring real cloud secrets.

Recommended approach:

| CI Step | Cost-Safe Approach |
|---|---|
| Python tests | Run locally in GitHub Actions |
| Linting | Run without external services |
| dbt parse | Run without warehouse execution where possible |
| dbt compile | Use local profile or mocked connection where possible |
| dbt build | Optional for CI unless a local service container is configured |

## Current MVP Cost Decision

The current project remains local because:

- the dataset is small;
- the business logic is still the main value;
- local execution is easier for reviewers;
- no real secrets are needed;
- no cloud account is required;
- cost is predictable and effectively zero.

## When to Move to Cloud

Move to Snowflake or BigQuery only after:

- Airflow DAG is stable;
- dbt build passes end-to-end;
- data quality summary exists;
- metrics are documented;
- runbook is complete;
- CI/CD is in place;
- README is strong;
- cost controls are documented.

## Estimated Cost of Current Validated Run

The latest validated local run included:

| Area | Result |
|---|---:|
| dbt executions | 207 |
| dbt tests | 178 |
| dbt warnings | 3 |
| dbt errors | 0 |
| Final marts | 5 |
| Snapshot rows | 15 |
| Product event rows | 1,842 |

Local cost for this run:

`$0`

## Production Cost Caveat

Actual production cost would depend on:

- data volume;
- schedule frequency;
- query concurrency;
- BI usage;
- retention policy;
- warehouse size;
- cloud provider pricing;
- regional pricing;
- monitoring requirements.

The figures in this document are directional estimates, not vendor quotes.

## Cost Strategy

The cost strategy for RevOpsPulse is:

1. Prove the pipeline locally.
2. Keep data small and synthetic.
3. Avoid cloud spend before the MVP is demonstrably valuable.
4. Move to cloud only when it adds portfolio signal.
5. Use strict auto-suspend, small compute and low schedule frequency.

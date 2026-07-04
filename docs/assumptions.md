# Assumptions

This document describes the main assumptions used in RevOpsPulse. The goal is to make the project defensible, reproducible and clear about what is intentionally simplified for a portfolio-grade MVP.

## Project Scope

RevOpsPulse is a synthetic modern data stack project for SaaS revenue, retention, product usage, marketing ROI and sales commission analytics.

The project is not connected to any real company, customer, employer system or internal dataset.

All data is synthetic and generated only for demonstration, testing and analytics engineering purposes.

## Data Volume Assumptions

The MVP uses a small synthetic dataset.

Latest validated row counts:

| Area | Validated Rows |
|---|---:|
| Accounts | 15 |
| Customers | 28 |
| Product events after incremental filter | 1,842 |
| Revenue months | 6 |
| Product usage days | 89 |
| Campaign/month rows | 33 |
| Sales rep/month rows | 18 |
| Subscription snapshot rows | 15 |

This volume is intentionally small so the project can run locally with Docker Compose and remain easy to inspect.

## Time Window Assumptions

The project simulates several months of SaaS activity.

Important date assumptions:

| Area | Assumption |
|---|---|
| Synthetic source data | Generated deterministically |
| Product events | Generated from a fixed start date and seed |
| API extraction | Uses `updated_since` for incremental extraction |
| Revenue metrics | Aggregated monthly |
| Product usage metrics | Aggregated daily |
| Marketing ROI | Aggregated by campaign and month |
| Sales commissions | Aggregated by sales rep and month |

## Source System Assumptions

RevOpsPulse models three main source types.

| Source | Assumption |
|---|---|
| PostgreSQL OLTP | Represents transactional billing, subscriptions, accounts, customers and sales targets |
| Mock CRM API | Represents leads, campaigns, opportunities and marketing spend |
| Product event files | Represents product usage events generated as JSON/NDJSON |

The mock API intentionally supports pagination, incremental extraction by timestamp and endpoint-based extraction.

## RAW Layer Assumptions

RAW files preserve extracted data with ingestion metadata.

Raw metadata includes:

| Field | Purpose |
|---|---|
| `source_system` | Identifies the source system |
| `source_entity` | Identifies source entity or endpoint |
| `batch_id` | Identifies extraction batch |
| `extracted_at` | Captures extraction timestamp |
| `load_date` | Captures load date |
| `raw_file_path` | Preserves file lineage |
| `record_hash` | Supports deduplication and lineage |

API and event records are also loaded into `raw.json_records` for dbt transformations.

## Revenue Assumptions

Revenue metrics are calculated from payment and invoice data.

Main assumptions:

| Metric | Assumption |
|---|---|
| Gross revenue | Successful payments attached to paid invoices |
| Net revenue | Gross successful paid revenue after refunds |
| MRR | Estimated from current active and past-due subscriptions |
| ARR | MRR multiplied by 12 |
| Payment failure rate | Failed payments divided by attempted payments |
| Refund rate | Refunded payments divided by attempted payments |

Trialing subscriptions may count as active accounts but do not contribute to MRR.

## MRR Limitation

MRR currently uses current subscription status and plan price.

A production implementation should calculate month-accurate MRR using subscription history or a subscription snapshot timeline.

This project includes `subscription_snapshot` to demonstrate SCD Type 2 capability, but the MVP revenue mart keeps MRR logic intentionally simple.

## Churn and Retention Assumptions

Churn is calculated from subscription cancellation timestamps.

Logo retention is calculated as:

`1 - churn_rate`

This is a simplified account-level logo retention approach.

The MVP does not yet calculate full cohort retention, GRR or NRR from historical subscription movements.

## Product Usage Assumptions

Product usage metrics are based on synthetic event data.

Supported events:

| Event | Meaning |
|---|---|
| `login` | User logged into the product |
| `account_created` | Account was created |
| `invite_user` | User invited another user |
| `create_project` | User created a project |
| `use_core_feature` | User used a core feature |
| `export_report` | User exported a report |
| `upgrade_prompt_viewed` | User saw an upgrade prompt |
| `billing_page_viewed` | User viewed billing page |
| `cancellation_started` | User started cancellation flow |

Activation events are defined as:

- `account_created`
- `invite_user`
- `create_project`
- `use_core_feature`

This is an intentionally simplified activation definition for the MVP.

## Marketing Attribution Assumptions

Marketing ROI is calculated at campaign/month level.

Main assumptions:

| Metric | Assumption |
|---|---|
| Cost per lead | Campaign spend divided by leads |
| CAC | Campaign spend divided by closed-won opportunities |
| Marketing ROI | Closed-won revenue minus spend, divided by spend |
| Lead conversion | Leads, opportunities and closed-won records joined by campaign |

Leads and opportunities can happen in different months.

Because of this, monthly conversion rates can exceed 1.0 in synthetic data. This is accepted as a known MVP limitation and documented in the metric definitions and data model docs.

## Sales Commission Assumptions

Sales commission metrics are calculated monthly by sales rep.

Commission eligibility requires:

- closed-won opportunity;
- paid invoice;
- succeeded payment.

Commission rules:

| Rule | Implementation |
|---|---|
| Base commission | 5% of net paid revenue |
| Accelerator | 8% on revenue above monthly target when quota attainment is at least 100% |
| Clawback | Refunds within 30 days reverse commission |
| Ineligible revenue | Failed payments, unpaid invoices and non-closed-won opportunities do not generate commission |

The MVP uses simplified account-level opportunity matching to attribute payments to sales reps.

Production systems may require split credit, ramp quotas, compensation plan versions, territory rules and legal payout audit trails.

## Data Quality Assumptions

The synthetic data intentionally includes a small number of data quality issues.

Known quality issues include:

| Issue | Purpose |
|---|---|
| Invalid subscription period | Demonstrates lifecycle validation |
| Negative net paid amount | Demonstrates monetary anomaly detection |
| Refund greater than payment | Demonstrates refund validation |

These issues are expected to produce dbt warnings, not build failures.

They are summarized in `mart_data_quality_summary`.

## Testing Assumptions

The project uses dbt tests to validate model integrity and business rules.

Test categories include:

| Category | Examples |
|---|---|
| Primary key integrity | `unique`, `not_null` |
| Referential integrity | `relationships` |
| Accepted values | statuses, event types and quality statuses |
| Monetary validation | `amount_non_negative`, `refund_not_greater_than_payment` |
| Temporal validation | `valid_subscription_period`, `event_timestamp_not_future` |
| Commission validation | commission eligibility rules represented in mart logic |

Known synthetic anomalies are configured as warnings where appropriate.

## Orchestration Assumptions

Airflow is used to orchestrate the local pipeline.

The DAG intentionally splits major stages into separate tasks instead of hiding the process in one large task.

The DAG validates orchestration of:

- Postgres extraction;
- API extraction;
- product event generation;
- event extraction;
- RAW JSON loading;
- dbt snapshot;
- dbt build.

## Local Runtime Assumptions

The project is designed for local execution with Docker Compose.

This keeps cost low and avoids requiring real cloud credentials for the MVP.

A production deployment would require a managed warehouse, external object storage, proper secrets management, observability and CI/CD deployment controls.

## Security Assumptions

No real customer, employer, banking, financial institution or internal company data is used.

Secrets should not be committed.

Configuration should use `.env.example`, environment variables and ignored local files such as `dbt/profiles.yml`.

## Non-Goals for the MVP

The MVP intentionally does not include:

- Kafka;
- Spark;
- Kubernetes;
- machine learning;
- real paid cloud infrastructure;
- complex frontend development;
- production-grade compensation plan engine;
- full multi-touch marketing attribution;
- real customer data.

These would add scope without improving the core employability signal of the MVP.

## Why These Assumptions Are Acceptable

The purpose of the project is to demonstrate employable analytics engineering patterns:

- reliable ingestion;
- orchestration with Airflow;
- dbt staging, intermediate and marts;
- dimensional modeling;
- incremental loading;
- snapshots;
- data quality tests;
- business metrics;
- documentation;
- reproducibility.

The assumptions keep the project focused, inspectable and defensible.

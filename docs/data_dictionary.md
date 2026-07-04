# Data Dictionary

This document describes the physical source tables, raw tables, analytics models and snapshot tables currently present in the RevOpsPulse local Postgres database.

The dictionary is generated from `information_schema.columns` to keep it aligned with the implemented database objects.

## Source Tables

### `source.accounts`

Synthetic OLTP account master data.

| Column | Type | Nullable |
|---|---|---|
| `account_id` | `text` | `NO` |
| `account_name` | `text` | `YES` |
| `industry` | `text` | `YES` |
| `company_size` | `text` | `YES` |
| `country` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### `source.customers`

Synthetic customer records associated with accounts.

| Column | Type | Nullable |
|---|---|---|
| `customer_id` | `text` | `NO` |
| `account_id` | `text` | `YES` |
| `email` | `text` | `YES` |
| `full_name` | `text` | `YES` |
| `country` | `text` | `YES` |
| `signup_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `is_deleted` | `boolean` | `YES` |

### `source.invoices`

Billing invoice records.

| Column | Type | Nullable |
|---|---|---|
| `invoice_id` | `text` | `NO` |
| `account_id` | `text` | `YES` |
| `subscription_id` | `text` | `YES` |
| `invoice_date` | `date` | `YES` |
| `due_date` | `date` | `YES` |
| `status` | `text` | `YES` |
| `currency` | `text` | `YES` |
| `amount_due` | `numeric` | `YES` |
| `amount_paid` | `numeric` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### `source.payments`

Payment attempts and outcomes.

| Column | Type | Nullable |
|---|---|---|
| `payment_id` | `text` | `NO` |
| `invoice_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `payment_date` | `timestamp without time zone` | `YES` |
| `payment_status` | `text` | `YES` |
| `payment_method` | `text` | `YES` |
| `amount` | `numeric` | `YES` |
| `currency` | `text` | `YES` |
| `failure_reason` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `source.plans`

Subscription plan catalog.

| Column | Type | Nullable |
|---|---|---|
| `plan_id` | `text` | `NO` |
| `plan_name` | `text` | `YES` |
| `billing_interval` | `text` | `YES` |
| `monthly_price` | `numeric` | `YES` |
| `currency` | `text` | `YES` |
| `is_active` | `boolean` | `YES` |

### `source.refunds`

Refund records associated with payments.

| Column | Type | Nullable |
|---|---|---|
| `refund_id` | `text` | `NO` |
| `payment_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `refund_date` | `timestamp without time zone` | `YES` |
| `amount` | `numeric` | `YES` |
| `reason` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `source.sales_reps`

Sales representative master data.

| Column | Type | Nullable |
|---|---|---|
| `sales_rep_id` | `text` | `NO` |
| `sales_rep_name` | `text` | `YES` |
| `team` | `text` | `YES` |
| `region` | `text` | `YES` |
| `hire_date` | `date` | `YES` |
| `is_active` | `boolean` | `YES` |

### `source.sales_targets`

Monthly sales targets by sales rep.

| Column | Type | Nullable |
|---|---|---|
| `target_id` | `text` | `NO` |
| `sales_rep_id` | `text` | `YES` |
| `target_month` | `date` | `YES` |
| `target_revenue` | `numeric` | `YES` |
| `target_new_customers` | `integer` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `source.subscriptions`

Subscription lifecycle records.

| Column | Type | Nullable |
|---|---|---|
| `subscription_id` | `text` | `NO` |
| `account_id` | `text` | `YES` |
| `plan_id` | `text` | `YES` |
| `subscription_status` | `text` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `ended_at` | `timestamp without time zone` | `YES` |
| `cancelled_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

## RAW Tables

### `raw.json_records`

Raw API and product event JSON payloads with ingestion metadata.

| Column | Type | Nullable |
|---|---|---|
| `source_system` | `text` | `NO` |
| `source_entity` | `text` | `NO` |
| `source_table_or_endpoint` | `text` | `NO` |
| `record_hash` | `text` | `NO` |
| `batch_id` | `text` | `NO` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `NO` |
| `source_file_path` | `text` | `YES` |
| `payload` | `jsonb` | `NO` |
| `loaded_at` | `timestamp with time zone` | `NO` |

## Analytics Models

### `analytics.dim_accounts`

Account dimension.

| Column | Type | Nullable |
|---|---|---|
| `account_id` | `text` | `YES` |
| `account_name` | `text` | `YES` |
| `industry` | `text` | `YES` |
| `company_size` | `text` | `YES` |
| `country` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### `analytics.dim_customers`

Customer dimension.

| Column | Type | Nullable |
|---|---|---|
| `customer_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `email` | `text` | `YES` |
| `full_name` | `text` | `YES` |
| `country` | `text` | `YES` |
| `signup_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `is_deleted` | `boolean` | `YES` |

### `analytics.dim_sales_reps`

Sales rep dimension.

| Column | Type | Nullable |
|---|---|---|
| `sales_rep_id` | `text` | `YES` |
| `sales_rep_name` | `text` | `YES` |
| `team` | `text` | `YES` |
| `region` | `text` | `YES` |
| `hire_date` | `date` | `YES` |
| `is_active` | `boolean` | `YES` |

### `analytics.fact_opportunities`

Opportunity fact enriched with sales and campaign context.

| Column | Type | Nullable |
|---|---|---|
| `opportunity_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `lead_id` | `text` | `YES` |
| `campaign_id` | `text` | `YES` |
| `sales_rep_id` | `text` | `YES` |
| `sales_rep_name` | `text` | `YES` |
| `sales_team` | `text` | `YES` |
| `sales_region` | `text` | `YES` |
| `opportunity_stage` | `text` | `YES` |
| `opportunity_amount` | `numeric` | `YES` |
| `probability` | `numeric` | `YES` |
| `close_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `lead_company_name` | `text` | `YES` |
| `lead_country` | `text` | `YES` |
| `lead_source` | `text` | `YES` |
| `lead_status` | `text` | `YES` |
| `campaign_name` | `text` | `YES` |
| `campaign_channel` | `text` | `YES` |
| `target_segment` | `text` | `YES` |
| `is_closed_won` | `boolean` | `YES` |
| `is_closed_lost` | `boolean` | `YES` |

### `analytics.fact_payments`

Payment fact enriched with invoice and refund context.

| Column | Type | Nullable |
|---|---|---|
| `payment_id` | `text` | `YES` |
| `invoice_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `subscription_id` | `text` | `YES` |
| `payment_date` | `timestamp without time zone` | `YES` |
| `payment_month` | `date` | `YES` |
| `payment_status` | `text` | `YES` |
| `payment_method` | `text` | `YES` |
| `payment_amount` | `numeric` | `YES` |
| `refunded_amount` | `numeric` | `YES` |
| `net_paid_amount` | `numeric` | `YES` |
| `invoice_status` | `text` | `YES` |
| `amount_due` | `numeric` | `YES` |
| `amount_paid` | `numeric` | `YES` |
| `first_refund_date` | `timestamp without time zone` | `YES` |
| `last_refund_date` | `timestamp without time zone` | `YES` |
| `is_successful_payment` | `boolean` | `YES` |
| `has_refund` | `boolean` | `YES` |
| `currency` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `analytics.fact_product_events`

Incremental product event fact keyed by event_id.

| Column | Type | Nullable |
|---|---|---|
| `event_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `user_id` | `text` | `YES` |
| `event_type` | `text` | `YES` |
| `event_timestamp` | `timestamp without time zone` | `YES` |
| `event_date` | `date` | `YES` |
| `session_id` | `text` | `YES` |
| `device_type` | `text` | `YES` |
| `country` | `text` | `YES` |
| `feature_name` | `text` | `YES` |
| `usage_count` | `integer` | `YES` |
| `report_type` | `text` | `YES` |
| `prompt_location` | `text` | `YES` |
| `cancellation_reason` | `text` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `source_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.int_opportunities_enriched`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `opportunity_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `lead_id` | `text` | `YES` |
| `campaign_id` | `text` | `YES` |
| `sales_rep_id` | `text` | `YES` |
| `sales_rep_name` | `text` | `YES` |
| `sales_team` | `text` | `YES` |
| `sales_region` | `text` | `YES` |
| `opportunity_stage` | `text` | `YES` |
| `opportunity_amount` | `numeric` | `YES` |
| `probability` | `numeric` | `YES` |
| `close_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `lead_company_name` | `text` | `YES` |
| `lead_country` | `text` | `YES` |
| `lead_source` | `text` | `YES` |
| `lead_status` | `text` | `YES` |
| `campaign_name` | `text` | `YES` |
| `campaign_channel` | `text` | `YES` |
| `target_segment` | `text` | `YES` |
| `is_closed_won` | `boolean` | `YES` |
| `is_closed_lost` | `boolean` | `YES` |
| `source_system` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.int_payments_enriched`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `payment_id` | `text` | `YES` |
| `invoice_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `subscription_id` | `text` | `YES` |
| `payment_date` | `timestamp without time zone` | `YES` |
| `payment_month` | `date` | `YES` |
| `payment_status` | `text` | `YES` |
| `payment_method` | `text` | `YES` |
| `payment_amount` | `numeric` | `YES` |
| `refunded_amount` | `numeric` | `YES` |
| `net_paid_amount` | `numeric` | `YES` |
| `invoice_status` | `text` | `YES` |
| `amount_due` | `numeric` | `YES` |
| `amount_paid` | `numeric` | `YES` |
| `first_refund_date` | `timestamp without time zone` | `YES` |
| `last_refund_date` | `timestamp without time zone` | `YES` |
| `is_successful_payment` | `boolean` | `YES` |
| `has_refund` | `boolean` | `YES` |
| `currency` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `analytics.int_product_usage_account_daily`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `account_id` | `text` | `YES` |
| `event_date` | `date` | `YES` |
| `total_events` | `bigint` | `YES` |
| `active_users` | `bigint` | `YES` |
| `sessions` | `bigint` | `YES` |
| `login_events` | `bigint` | `YES` |
| `core_feature_events` | `bigint` | `YES` |
| `project_created_events` | `bigint` | `YES` |
| `invite_user_events` | `bigint` | `YES` |
| `export_report_events` | `bigint` | `YES` |
| `upgrade_prompt_viewed_events` | `bigint` | `YES` |
| `billing_page_viewed_events` | `bigint` | `YES` |
| `cancellation_started_events` | `bigint` | `YES` |
| `total_feature_usage_count` | `bigint` | `YES` |
| `first_event_at` | `timestamp without time zone` | `YES` |
| `last_event_at` | `timestamp without time zone` | `YES` |

### `analytics.mart_data_quality_summary`

Data quality check summary with business impact.

| Column | Type | Nullable |
|---|---|---|
| `run_date` | `date` | `YES` |
| `source_name` | `text` | `YES` |
| `model_name` | `text` | `YES` |
| `test_name` | `text` | `YES` |
| `severity` | `text` | `YES` |
| `status` | `text` | `YES` |
| `failed_records` | `bigint` | `YES` |
| `total_records` | `bigint` | `YES` |
| `failure_rate` | `numeric` | `YES` |
| `business_impact` | `text` | `YES` |
| `created_at` | `timestamp with time zone` | `YES` |

### `analytics.mart_marketing_roi_monthly`

Monthly campaign ROI, CAC and funnel metrics.

| Column | Type | Nullable |
|---|---|---|
| `metric_month` | `date` | `YES` |
| `campaign_id` | `text` | `YES` |
| `campaign_name` | `text` | `YES` |
| `channel` | `text` | `YES` |
| `target_segment` | `text` | `YES` |
| `marketing_spend` | `numeric` | `YES` |
| `leads_count` | `bigint` | `YES` |
| `opportunities_count` | `bigint` | `YES` |
| `closed_won_opportunities` | `bigint` | `YES` |
| `pipeline_amount` | `numeric` | `YES` |
| `closed_won_revenue` | `numeric` | `YES` |
| `cost_per_lead` | `numeric` | `YES` |
| `cac` | `numeric` | `YES` |
| `lead_to_opportunity_conversion_rate` | `numeric` | `YES` |
| `lead_to_closed_won_rate` | `numeric` | `YES` |
| `marketing_roi` | `numeric` | `YES` |
| `created_at` | `timestamp with time zone` | `YES` |

### `analytics.mart_product_usage_daily`

Daily product usage, activation and adoption metrics.

| Column | Type | Nullable |
|---|---|---|
| `usage_date` | `date` | `YES` |
| `total_events` | `bigint` | `YES` |
| `active_accounts` | `bigint` | `YES` |
| `inactive_accounts` | `bigint` | `YES` |
| `active_users` | `bigint` | `YES` |
| `login_events` | `bigint` | `YES` |
| `account_created_events` | `bigint` | `YES` |
| `invite_user_events` | `bigint` | `YES` |
| `create_project_events` | `bigint` | `YES` |
| `core_feature_events` | `bigint` | `YES` |
| `export_report_events` | `bigint` | `YES` |
| `upgrade_prompt_views` | `bigint` | `YES` |
| `billing_page_views` | `bigint` | `YES` |
| `cancellation_started_events` | `bigint` | `YES` |
| `activated_accounts` | `bigint` | `YES` |
| `core_feature_accounts` | `bigint` | `YES` |
| `report_export_accounts` | `bigint` | `YES` |
| `cancellation_started_accounts` | `bigint` | `YES` |
| `activation_rate` | `numeric` | `YES` |
| `core_feature_adoption_rate` | `numeric` | `YES` |
| `report_export_adoption_rate` | `numeric` | `YES` |
| `cancellation_intent_rate` | `numeric` | `YES` |
| `created_at` | `timestamp with time zone` | `YES` |

### `analytics.mart_revenue_monthly`

Monthly SaaS revenue, MRR, churn and payment quality metrics.

| Column | Type | Nullable |
|---|---|---|
| `metric_month` | `date` | `YES` |
| `paid_invoice_count` | `bigint` | `YES` |
| `paying_accounts` | `bigint` | `YES` |
| `gross_revenue` | `numeric` | `YES` |
| `refund_amount` | `numeric` | `YES` |
| `net_revenue` | `numeric` | `YES` |
| `active_accounts` | `bigint` | `YES` |
| `active_subscriptions` | `bigint` | `YES` |
| `mrr` | `numeric` | `YES` |
| `arr` | `numeric` | `YES` |
| `churned_accounts` | `bigint` | `YES` |
| `churned_subscriptions` | `bigint` | `YES` |
| `attempted_payments` | `bigint` | `YES` |
| `failed_payments` | `bigint` | `YES` |
| `refunded_payments` | `bigint` | `YES` |
| `payment_failure_rate` | `numeric` | `YES` |
| `refund_rate` | `numeric` | `YES` |
| `churn_rate` | `numeric` | `YES` |
| `logo_retention_rate` | `numeric` | `YES` |
| `created_at` | `timestamp with time zone` | `YES` |

### `analytics.mart_sales_commissions_monthly`

Monthly sales commission and incentive metrics by sales rep.

| Column | Type | Nullable |
|---|---|---|
| `commission_month` | `date` | `YES` |
| `sales_rep_id` | `text` | `YES` |
| `sales_rep_name` | `text` | `YES` |
| `sales_team` | `text` | `YES` |
| `sales_region` | `text` | `YES` |
| `target_revenue` | `numeric` | `YES` |
| `target_new_customers` | `integer` | `YES` |
| `attributed_payments` | `bigint` | `YES` |
| `eligible_payments` | `bigint` | `YES` |
| `ineligible_payments` | `bigint` | `YES` |
| `gross_paid_revenue` | `numeric` | `YES` |
| `refunded_revenue` | `numeric` | `YES` |
| `commissionable_revenue` | `numeric` | `YES` |
| `clawback_revenue` | `numeric` | `YES` |
| `quota_attainment` | `numeric` | `YES` |
| `above_quota_revenue` | `numeric` | `YES` |
| `base_commission_amount` | `numeric` | `YES` |
| `accelerator_commission_amount` | `numeric` | `YES` |
| `clawback_amount` | `numeric` | `YES` |
| `commission_payout` | `numeric` | `YES` |
| `commission_accuracy_rate` | `numeric` | `YES` |
| `created_at` | `timestamp with time zone` | `YES` |

### `analytics.stg_api__campaigns`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `campaign_id` | `text` | `YES` |
| `campaign_name` | `text` | `YES` |
| `channel` | `text` | `YES` |
| `target_segment` | `text` | `YES` |
| `start_date` | `date` | `YES` |
| `end_date` | `date` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `source_table_or_endpoint` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.stg_api__leads`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `lead_id` | `text` | `YES` |
| `campaign_id` | `text` | `YES` |
| `company_name` | `text` | `YES` |
| `email` | `text` | `YES` |
| `country` | `text` | `YES` |
| `lead_source` | `text` | `YES` |
| `lead_status` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `source_table_or_endpoint` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.stg_api__marketing_spend`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `spend_id` | `text` | `YES` |
| `campaign_id` | `text` | `YES` |
| `spend_date` | `date` | `YES` |
| `amount` | `numeric` | `YES` |
| `currency` | `text` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `source_table_or_endpoint` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.stg_api__opportunities`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `opportunity_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `lead_id` | `text` | `YES` |
| `campaign_id` | `text` | `YES` |
| `sales_rep_id` | `text` | `YES` |
| `opportunity_stage` | `text` | `YES` |
| `amount` | `numeric` | `YES` |
| `probability` | `numeric` | `YES` |
| `close_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `source_table_or_endpoint` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.stg_events__product_events`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `event_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `user_id` | `text` | `YES` |
| `event_type` | `text` | `YES` |
| `event_timestamp` | `timestamp without time zone` | `YES` |
| `event_date` | `date` | `YES` |
| `session_id` | `text` | `YES` |
| `device_type` | `text` | `YES` |
| `country` | `text` | `YES` |
| `feature_name` | `text` | `YES` |
| `usage_count` | `integer` | `YES` |
| `report_type` | `text` | `YES` |
| `prompt_location` | `text` | `YES` |
| `cancellation_reason` | `text` | `YES` |
| `source_system` | `text` | `YES` |
| `source_entity` | `text` | `YES` |
| `source_table_or_endpoint` | `text` | `YES` |
| `batch_id` | `text` | `YES` |
| `extracted_at` | `timestamp with time zone` | `YES` |
| `load_date` | `date` | `YES` |
| `raw_file_path` | `text` | `YES` |
| `source_file_path` | `text` | `YES` |
| `record_hash` | `text` | `YES` |

### `analytics.stg_postgres__accounts`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `account_id` | `text` | `YES` |
| `account_name` | `text` | `YES` |
| `industry` | `text` | `YES` |
| `company_size` | `text` | `YES` |
| `country` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### `analytics.stg_postgres__customers`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `customer_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `email` | `text` | `YES` |
| `full_name` | `text` | `YES` |
| `country` | `text` | `YES` |
| `signup_date` | `date` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `is_deleted` | `boolean` | `YES` |

### `analytics.stg_postgres__invoices`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `invoice_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `subscription_id` | `text` | `YES` |
| `invoice_status` | `text` | `YES` |
| `invoice_date` | `date` | `YES` |
| `due_date` | `date` | `YES` |
| `currency` | `text` | `YES` |
| `amount_due` | `numeric` | `YES` |
| `amount_paid` | `numeric` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### `analytics.stg_postgres__payments`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `payment_id` | `text` | `YES` |
| `invoice_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `payment_date` | `timestamp without time zone` | `YES` |
| `payment_status` | `text` | `YES` |
| `payment_method` | `text` | `YES` |
| `amount` | `numeric` | `YES` |
| `currency` | `text` | `YES` |
| `failure_reason` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `analytics.stg_postgres__plans`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `plan_id` | `text` | `YES` |
| `plan_name` | `text` | `YES` |
| `billing_interval` | `text` | `YES` |
| `monthly_price` | `numeric` | `YES` |
| `currency` | `text` | `YES` |
| `is_active` | `boolean` | `YES` |

### `analytics.stg_postgres__refunds`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `refund_id` | `text` | `YES` |
| `payment_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `refund_date` | `timestamp without time zone` | `YES` |
| `amount` | `numeric` | `YES` |
| `refund_reason` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `analytics.stg_postgres__sales_reps`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `sales_rep_id` | `text` | `YES` |
| `sales_rep_name` | `text` | `YES` |
| `team` | `text` | `YES` |
| `region` | `text` | `YES` |
| `hire_date` | `date` | `YES` |
| `is_active` | `boolean` | `YES` |

### `analytics.stg_postgres__sales_targets`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `target_id` | `text` | `YES` |
| `sales_rep_id` | `text` | `YES` |
| `target_month` | `date` | `YES` |
| `target_revenue` | `numeric` | `YES` |
| `target_new_customers` | `integer` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |

### `analytics.stg_postgres__subscriptions`

Database object in the RevOpsPulse data model.

| Column | Type | Nullable |
|---|---|---|
| `subscription_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `plan_id` | `text` | `YES` |
| `subscription_status` | `text` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `ended_at` | `timestamp without time zone` | `YES` |
| `cancelled_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

## Snapshot Tables

### `snapshots.subscription_snapshot`

SCD Type 2 snapshot of subscription records.

| Column | Type | Nullable |
|---|---|---|
| `subscription_id` | `text` | `YES` |
| `account_id` | `text` | `YES` |
| `plan_id` | `text` | `YES` |
| `subscription_status` | `text` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `ended_at` | `timestamp without time zone` | `YES` |
| `cancelled_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `dbt_scd_id` | `text` | `YES` |
| `dbt_updated_at` | `timestamp without time zone` | `YES` |
| `dbt_valid_from` | `timestamp without time zone` | `YES` |
| `dbt_valid_to` | `timestamp without time zone` | `YES` |

## Notes

- Source tables represent synthetic OLTP and CRM-like operational data.
- RAW tables preserve ingestion metadata and JSON payload lineage.
- Analytics models are dbt-created views or tables under the `analytics` schema.
- `fact_product_events` is the main incremental fact table.
- `subscription_snapshot` demonstrates SCD Type 2 tracking using dbt snapshots.
- This project uses synthetic data only and does not contain real customer or employer data.

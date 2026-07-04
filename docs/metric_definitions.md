# Metric Definitions

This document defines the core SaaS, product usage, marketing ROI, sales commission and data quality metrics implemented in RevOpsPulse.

## Source of Truth

| Metric Area | dbt Model |
|---|---|
| Revenue | `mart_revenue_monthly` |
| Product Usage | `mart_product_usage_daily` |
| Marketing ROI | `mart_marketing_roi_monthly` |
| Sales Commissions | `mart_sales_commissions_monthly` |
| Data Quality | `mart_data_quality_summary` |

## Revenue Metrics

### Gross Revenue

Model: `mart_revenue_monthly`
Column: `gross_revenue`

Total successful paid invoice amount before refunds.

Formula: `sum(payment_amount)`

Only payments where `payment_status = 'succeeded'` and `invoice_status = 'paid'` are included.

### Net Revenue

Model: `mart_revenue_monthly`
Column: `net_revenue`

Revenue after refunds.

Formula: `sum(net_paid_amount)`

Only successful paid invoices are included.

### Refund Amount

Model: `mart_revenue_monthly`
Column: `refund_amount`

Total refunded amount for successful paid invoices.

Formula: `sum(refunded_amount)`

### MRR

Model: `mart_revenue_monthly`
Column: `mrr`

Monthly recurring revenue estimated from active and past-due subscriptions.

Formula: `sum(monthly_price)`

Included subscription statuses:

- `active`
- `past_due`

Trialing subscriptions count as active accounts but do not contribute to MRR.

### ARR

Model: `mart_revenue_monthly`
Column: `arr`

Annualized recurring revenue.

Formula: `mrr * 12`

### Payment Failure Rate

Model: `mart_revenue_monthly`
Column: `payment_failure_rate`

Share of attempted payments that failed.

Formula: `failed_payments / attempted_payments`

### Refund Rate

Model: `mart_revenue_monthly`
Column: `refund_rate`

Share of attempted payments with at least one refund.

Formula: `refunded_payments / attempted_payments`

### Churned Accounts

Model: `mart_revenue_monthly`
Column: `churned_accounts`

Distinct accounts with `cancelled_at` in the metric month.

### Churn Rate

Model: `mart_revenue_monthly`
Column: `churn_rate`

Formula: `churned_accounts / active_accounts`

### Logo Retention Rate

Model: `mart_revenue_monthly`
Column: `logo_retention_rate`

Formula: `1 - churn_rate`

## Product Usage Metrics

### Total Events

Model: `mart_product_usage_daily`
Column: `total_events`

Total product events observed per day.

### Active Accounts

Model: `mart_product_usage_daily`
Column: `active_accounts`

Distinct accounts with at least one product event on the usage date.

### Inactive Accounts

Model: `mart_product_usage_daily`
Column: `inactive_accounts`

Total accounts minus active accounts.

Formula: `total_accounts - active_accounts`

### Active Users

Model: `mart_product_usage_daily`
Column: `active_users`

Distinct users with at least one product event on the usage date.

### Activation Rate

Model: `mart_product_usage_daily`
Column: `activation_rate`

Share of accounts with at least one activation-related event on the usage date.

Activation events:

- `account_created`
- `invite_user`
- `create_project`
- `use_core_feature`

Formula: `activated_accounts / total_accounts`

### Core Feature Adoption Rate

Model: `mart_product_usage_daily`
Column: `core_feature_adoption_rate`

Share of accounts that used a core feature on the usage date.

Formula: `core_feature_accounts / total_accounts`

### Report Export Adoption Rate

Model: `mart_product_usage_daily`
Column: `report_export_adoption_rate`

Share of accounts that exported a report on the usage date.

Formula: `report_export_accounts / total_accounts`

### Cancellation Intent Rate

Model: `mart_product_usage_daily`
Column: `cancellation_intent_rate`

Share of accounts that started a cancellation flow on the usage date.

Formula: `cancellation_started_accounts / total_accounts`

## Marketing Metrics

### Marketing Spend

Model: `mart_marketing_roi_monthly`
Column: `marketing_spend`

Monthly campaign spend from the marketing spend API source.

### Leads Count

Model: `mart_marketing_roi_monthly`
Column: `leads_count`

Distinct leads created in the month by campaign.

### Opportunities Count

Model: `mart_marketing_roi_monthly`
Column: `opportunities_count`

Distinct opportunities attributed to the campaign/month.

### Closed-Won Opportunities

Model: `mart_marketing_roi_monthly`
Column: `closed_won_opportunities`

Distinct opportunities where `is_closed_won = true`.

### Closed-Won Revenue

Model: `mart_marketing_roi_monthly`
Column: `closed_won_revenue`

Sum of opportunity amount for closed-won opportunities.

### Cost per Lead

Model: `mart_marketing_roi_monthly`
Column: `cost_per_lead`

Formula: `marketing_spend / leads_count`

### CAC

Model: `mart_marketing_roi_monthly`
Column: `cac`

Customer acquisition cost estimated at campaign/month level.

Formula: `marketing_spend / closed_won_opportunities`

### Lead-to-Opportunity Conversion Rate

Model: `mart_marketing_roi_monthly`
Column: `lead_to_opportunity_conversion_rate`

Formula: `opportunities_count / leads_count`

### Lead-to-Closed-Won Rate

Model: `mart_marketing_roi_monthly`
Column: `lead_to_closed_won_rate`

Formula: `closed_won_opportunities / leads_count`

### Marketing ROI

Model: `mart_marketing_roi_monthly`
Column: `marketing_roi`

Formula: `(closed_won_revenue - marketing_spend) / marketing_spend`

## Sales Commission Metrics

### Commissionable Revenue

Model: `mart_sales_commissions_monthly`
Column: `commissionable_revenue`

Revenue eligible for commission.

Eligibility rules:

- opportunity is closed-won;
- payment succeeded;
- invoice is paid.

### Quota Attainment

Model: `mart_sales_commissions_monthly`
Column: `quota_attainment`

Formula: `commissionable_revenue / target_revenue`

If target revenue is zero or missing, quota attainment is set to `0`.

### Base Commission Amount

Model: `mart_sales_commissions_monthly`
Column: `base_commission_amount`

Base commission is 5% of commissionable revenue.

Formula: `commissionable_revenue * 0.05`

### Above-Quota Revenue

Model: `mart_sales_commissions_monthly`
Column: `above_quota_revenue`

Revenue above the monthly sales target.

Formula: `greatest(commissionable_revenue - target_revenue, 0)`

### Accelerator Commission Amount

Model: `mart_sales_commissions_monthly`
Column: `accelerator_commission_amount`

If the sales rep reaches at least 100% quota attainment, revenue above quota earns 8%.

Formula: `above_quota_revenue * 0.08`

### Clawback Amount

Model: `mart_sales_commissions_monthly`
Column: `clawback_amount`

Commission reversal for refunds within 30 days.

Formula: `refunded_amount * 0.05`

### Commission Payout

Model: `mart_sales_commissions_monthly`
Column: `commission_payout`

Final commission payout after clawbacks.

Formula: `greatest(base_commission_amount + accelerator_commission_amount - clawback_amount, 0)`

### Commission Accuracy Rate

Model: `mart_sales_commissions_monthly`
Column: `commission_accuracy_rate`

Share of attributed payments that are eligible for commission.

Formula: `eligible_payments / attributed_payments`

## Data Quality Metrics

### Failed Records

Model: `mart_data_quality_summary`
Column: `failed_records`

Number of records failing a specific data quality check.

### Total Records

Model: `mart_data_quality_summary`
Column: `total_records`

Number of records evaluated by the check.

### Failure Rate

Model: `mart_data_quality_summary`
Column: `failure_rate`

Formula: `failed_records / total_records`

### Status

Model: `mart_data_quality_summary`
Column: `status`

Allowed values:

- `pass`
- `warn`
- `fail`

## Known Limitations

MRR is calculated from current subscription status and plan price. A production implementation should use historical subscription snapshots for month-accurate MRR.

Marketing attribution uses campaign-level relationships and month-level aggregation. Because leads and opportunities can occur in different months, some monthly conversion rates can exceed 1.0 in synthetic data.

Commission logic uses a simplified single-rep attribution model based on account-level opportunity matching. Production systems may require split credit, ramping quotas, territory rules and compensation plan versioning.

Synthetic data intentionally includes some quality issues to demonstrate dbt tests and the data quality mart.

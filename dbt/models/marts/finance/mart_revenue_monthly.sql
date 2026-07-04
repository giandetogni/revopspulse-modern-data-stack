with payment_bounds as (
    select
        date_trunc('month', min(payment_date))::date as min_month,
        date_trunc('month', max(payment_date))::date as max_month
    from {{ ref('fact_payments') }}
),

month_spine as (
    select generate_series(
        min_month,
        max_month,
        interval '1 month'
    )::date as metric_month
    from payment_bounds
),

valid_payments as (
    select *
    from {{ ref('fact_payments') }}
    where payment_status = 'succeeded'
      and invoice_status = 'paid'
),

payment_monthly as (
    select
        date_trunc('month', payment_date)::date as metric_month,
        count(*) as paid_invoice_count,
        count(distinct account_id) as paying_accounts,
        sum(payment_amount) as gross_revenue,
        sum(refunded_amount) as refund_amount,
        sum(net_paid_amount) as net_revenue
    from valid_payments
    group by 1
),

payment_quality_monthly as (
    select
        date_trunc('month', payment_date)::date as metric_month,
        count(*) as attempted_payments,
        count(*) filter (where payment_status = 'failed') as failed_payments,
        count(*) filter (where has_refund) as refunded_payments
    from {{ ref('fact_payments') }}
    group by 1
),

subscription_monthly as (
    select
        m.metric_month,
        count(distinct s.account_id) filter (
            where s.subscription_status in ('active', 'past_due', 'trialing')
        ) as active_accounts,
        count(distinct s.subscription_id) filter (
            where s.subscription_status in ('active', 'past_due', 'trialing')
        ) as active_subscriptions,
        sum(
            case
                when s.subscription_status in ('active', 'past_due') then p.monthly_price
                else 0
            end
        ) as mrr
    from month_spine m
    left join {{ ref('stg_postgres__subscriptions') }} s
        on s.started_at::date <= (m.metric_month + interval '1 month - 1 day')::date
        and coalesce(s.ended_at::date, date '9999-12-31') >= m.metric_month
    left join {{ ref('stg_postgres__plans') }} p
        on s.plan_id = p.plan_id
    group by 1
),

churn_monthly as (
    select
        date_trunc('month', cancelled_at)::date as metric_month,
        count(distinct account_id) as churned_accounts,
        count(distinct subscription_id) as churned_subscriptions
    from {{ ref('stg_postgres__subscriptions') }}
    where cancelled_at is not null
    group by 1
),

final as (
    select
        m.metric_month,

        coalesce(p.paid_invoice_count, 0) as paid_invoice_count,
        coalesce(p.paying_accounts, 0) as paying_accounts,
        coalesce(p.gross_revenue, 0) as gross_revenue,
        coalesce(p.refund_amount, 0) as refund_amount,
        coalesce(p.net_revenue, 0) as net_revenue,

        coalesce(s.active_accounts, 0) as active_accounts,
        coalesce(s.active_subscriptions, 0) as active_subscriptions,
        coalesce(s.mrr, 0) as mrr,
        coalesce(s.mrr, 0) * 12 as arr,

        coalesce(c.churned_accounts, 0) as churned_accounts,
        coalesce(c.churned_subscriptions, 0) as churned_subscriptions,

        coalesce(q.attempted_payments, 0) as attempted_payments,
        coalesce(q.failed_payments, 0) as failed_payments,
        coalesce(q.refunded_payments, 0) as refunded_payments,

        coalesce(
            round(
                coalesce(q.failed_payments, 0)::numeric
                / nullif(q.attempted_payments, 0),
                4
            ),
            0
        ) as payment_failure_rate,

        coalesce(
            round(
                coalesce(q.refunded_payments, 0)::numeric
                / nullif(q.attempted_payments, 0),
                4
            ),
            0
        ) as refund_rate,

        coalesce(
            round(
                coalesce(c.churned_accounts, 0)::numeric
                / nullif(s.active_accounts, 0),
                4
            ),
            0
        ) as churn_rate,

        coalesce(
            round(
                1 - (
                    coalesce(c.churned_accounts, 0)::numeric
                    / nullif(s.active_accounts, 0)
                ),
                4
            ),
            1
        ) as logo_retention_rate,

        current_timestamp as created_at
    from month_spine m
    left join payment_monthly p
        on m.metric_month = p.metric_month
    left join payment_quality_monthly q
        on m.metric_month = q.metric_month
    left join subscription_monthly s
        on m.metric_month = s.metric_month
    left join churn_monthly c
        on m.metric_month = c.metric_month
)

select *
from final

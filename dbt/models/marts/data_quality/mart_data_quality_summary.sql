with checks as (
    select
        current_date as run_date,
        'postgres' as source_name,
        'fact_payments' as model_name,
        'amount_non_negative' as test_name,
        'warn' as severity,
        count(*) filter (where net_paid_amount < 0) as failed_records,
        count(*) as total_records,
        'Negative net paid amount can distort revenue, refund and commission metrics.' as business_impact
    from {{ ref('fact_payments') }}

    union all

    select
        current_date as run_date,
        'postgres' as source_name,
        'stg_postgres__subscriptions' as model_name,
        'valid_subscription_period' as test_name,
        'warn' as severity,
        count(*) filter (
            where ended_at is not null
              and started_at is not null
              and ended_at < started_at
        ) as failed_records,
        count(*) as total_records,
        'Invalid subscription periods can distort churn, retention and lifecycle metrics.' as business_impact
    from {{ ref('stg_postgres__subscriptions') }}

    union all

    select
        current_date as run_date,
        'postgres' as source_name,
        'fact_payments' as model_name,
        'refund_not_greater_than_payment' as test_name,
        'warn' as severity,
        count(*) filter (where refunded_amount > payment_amount) as failed_records,
        count(*) as total_records,
        'Refunds greater than payments can distort net revenue and clawback calculations.' as business_impact
    from {{ ref('fact_payments') }}

    union all

    select
        current_date as run_date,
        'product_events' as source_name,
        'fact_product_events' as model_name,
        'event_timestamp_not_future' as test_name,
        'error' as severity,
        count(*) filter (where event_timestamp > current_timestamp) as failed_records,
        count(*) as total_records,
        'Future event timestamps can distort activation, adoption and retention metrics.' as business_impact
    from {{ ref('fact_product_events') }}
)

select
    run_date,
    source_name,
    model_name,
    test_name,
    severity,
    case
        when failed_records = 0 then 'pass'
        when severity = 'warn' then 'warn'
        else 'fail'
    end as status,
    failed_records,
    total_records,
    round(failed_records::numeric / nullif(total_records, 0), 4) as failure_rate,
    business_impact,
    current_timestamp as created_at
from checks

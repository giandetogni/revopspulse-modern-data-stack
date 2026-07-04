with payments as (
    select * from {{ ref('stg_postgres__payments') }}
),

invoices as (
    select * from {{ ref('stg_postgres__invoices') }}
),

refunds as (
    select
        payment_id,
        account_id,
        sum(amount) as refunded_amount,
        min(refund_date) as first_refund_date,
        max(refund_date) as last_refund_date
    from {{ ref('stg_postgres__refunds') }}
    group by 1, 2
)

select
    payments.payment_id,
    payments.invoice_id,
    payments.account_id,
    invoices.subscription_id,
    payments.payment_date,
    date_trunc('month', payments.payment_date)::date as payment_month,
    payments.payment_status,
    payments.payment_method,
    payments.amount as payment_amount,
    coalesce(refunds.refunded_amount, 0) as refunded_amount,
    payments.amount - coalesce(refunds.refunded_amount, 0) as net_paid_amount,
    invoices.invoice_status,
    invoices.amount_due,
    invoices.amount_paid,
    refunds.first_refund_date,
    refunds.last_refund_date,
    case
        when payments.payment_status = 'succeeded' then true
        else false
    end as is_successful_payment,
    case
        when coalesce(refunds.refunded_amount, 0) > 0 then true
        else false
    end as has_refund,
    payments.currency,
    payments.created_at
from payments
left join invoices
    on payments.invoice_id = invoices.invoice_id
left join refunds
    on payments.payment_id = refunds.payment_id

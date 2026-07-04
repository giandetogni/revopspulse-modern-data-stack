select
    payment_id,
    invoice_id,
    account_id,
    cast(payment_date as timestamp) as payment_date,
    payment_status,
    payment_method,
    cast(amount as numeric(12, 2)) as amount,
    currency,
    failure_reason,
    cast(created_at as timestamp) as created_at
from {{ source('postgres_source', 'payments') }}

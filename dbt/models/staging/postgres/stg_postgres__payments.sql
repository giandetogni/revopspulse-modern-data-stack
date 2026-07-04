select
    payment_id,
    invoice_id,
    account_id,
    payment_status,
    payment_method,
    cast(payment_date as timestamp) as payment_date,
    cast(amount as numeric(12, 2)) as amount,
    currency,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'payments') }}

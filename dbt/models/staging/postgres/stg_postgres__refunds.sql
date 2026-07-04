select
    refund_id,
    payment_id,
    account_id,
    refund_reason,
    cast(refund_date as timestamp) as refund_date,
    cast(amount as numeric(12, 2)) as amount,
    currency,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'refunds') }}

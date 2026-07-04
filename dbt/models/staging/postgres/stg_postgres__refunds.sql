select
    refund_id,
    payment_id,
    account_id,
    cast(refund_date as timestamp) as refund_date,
    cast(amount as numeric(12, 2)) as amount,
    reason as refund_reason,
    cast(created_at as timestamp) as created_at
from {{ source('postgres_source', 'refunds') }}

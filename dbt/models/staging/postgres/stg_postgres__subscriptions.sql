select
    subscription_id,
    account_id,
    plan_id,
    status as subscription_status,
    cast(started_at as timestamp) as started_at,
    cast(ended_at as timestamp) as ended_at,
    cast(mrr as numeric(12, 2)) as mrr,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'subscriptions') }}

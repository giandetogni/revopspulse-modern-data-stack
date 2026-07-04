select
    subscription_id,
    account_id,
    plan_id,
    subscription_status,
    cast(started_at as timestamp) as started_at,
    cast(ended_at as timestamp) as ended_at,
    cast(cancelled_at as timestamp) as cancelled_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'subscriptions') }}

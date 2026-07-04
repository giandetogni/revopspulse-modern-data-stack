select
    plan_id,
    plan_name,
    billing_interval,
    cast(monthly_price as numeric(12, 2)) as monthly_price,
    currency,
    is_active
from {{ source('postgres_source', 'plans') }}

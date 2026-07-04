select
    plan_id,
    plan_name,
    billing_interval,
    cast(monthly_price as numeric(12, 2)) as monthly_price,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'plans') }}

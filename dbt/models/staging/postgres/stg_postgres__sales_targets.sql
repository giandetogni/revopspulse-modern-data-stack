select
    sales_rep_id,
    cast(target_month as date) as target_month,
    cast(monthly_quota as numeric(12, 2)) as monthly_quota,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'sales_targets') }}

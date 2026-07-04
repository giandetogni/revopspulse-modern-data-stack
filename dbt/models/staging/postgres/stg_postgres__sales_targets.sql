select
    target_id,
    sales_rep_id,
    cast(target_month as date) as target_month,
    cast(target_revenue as numeric(12, 2)) as target_revenue,
    target_new_customers,
    cast(created_at as timestamp) as created_at
from {{ source('postgres_source', 'sales_targets') }}

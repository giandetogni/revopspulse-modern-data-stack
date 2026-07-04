select
    sales_rep_id,
    sales_rep_name,
    region,
    manager_name,
    cast(hire_date as date) as hire_date,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'sales_reps') }}

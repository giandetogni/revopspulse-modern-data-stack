select
    sales_rep_id,
    sales_rep_name,
    team,
    region,
    cast(hire_date as date) as hire_date,
    is_active
from {{ source('postgres_source', 'sales_reps') }}

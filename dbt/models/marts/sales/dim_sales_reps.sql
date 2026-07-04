select
    sales_rep_id,
    sales_rep_name,
    team,
    region,
    hire_date,
    is_active
from {{ ref('stg_postgres__sales_reps') }}

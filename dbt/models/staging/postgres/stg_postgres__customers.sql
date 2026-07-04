select
    customer_id,
    account_id,
    first_name,
    last_name,
    email,
    job_title,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'customers') }}

select
    customer_id,
    account_id,
    email,
    full_name,
    country,
    cast(signup_date as date) as signup_date,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at,
    is_deleted
from {{ source('postgres_source', 'customers') }}

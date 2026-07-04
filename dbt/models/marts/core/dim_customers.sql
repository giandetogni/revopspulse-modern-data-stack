select
    customer_id,
    account_id,
    email,
    full_name,
    country,
    signup_date,
    created_at,
    updated_at,
    is_deleted
from {{ ref('stg_postgres__customers') }}

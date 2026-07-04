select
    account_id,
    account_name,
    industry,
    company_size,
    country,
    created_at,
    updated_at
from {{ ref('stg_postgres__accounts') }}

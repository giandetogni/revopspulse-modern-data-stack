select
    account_id,
    account_name,
    industry,
    company_size,
    country,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'accounts') }}

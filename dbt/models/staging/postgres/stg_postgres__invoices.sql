select
    invoice_id,
    account_id,
    subscription_id,
    status as invoice_status,
    cast(invoice_date as date) as invoice_date,
    cast(due_date as date) as due_date,
    currency,
    cast(amount_due as numeric(12, 2)) as amount_due,
    cast(amount_paid as numeric(12, 2)) as amount_paid,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('postgres_source', 'invoices') }}

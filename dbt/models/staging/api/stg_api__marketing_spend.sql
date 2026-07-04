select
    payload->>'spend_id' as spend_id,
    payload->>'campaign_id' as campaign_id,
    cast(payload->>'spend_date' as date) as spend_date,
    cast(payload->>'amount' as numeric(12, 2)) as amount,
    payload->>'currency' as currency,
    cast(payload->>'updated_at' as timestamp) as updated_at,
    source_system,
    source_entity,
    source_table_or_endpoint,
    batch_id,
    extracted_at,
    load_date,
    raw_file_path,
    record_hash
from {{ source('raw_warehouse', 'json_records') }}
where source_system = 'mock_crm_api'
  and source_entity = 'marketing_spend'

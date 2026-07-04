select
    payload->>'opportunity_id' as opportunity_id,
    payload->>'account_id' as account_id,
    payload->>'lead_id' as lead_id,
    payload->>'campaign_id' as campaign_id,
    payload->>'sales_rep_id' as sales_rep_id,
    payload->>'stage' as opportunity_stage,
    cast(payload->>'amount' as numeric(12, 2)) as amount,
    cast(payload->>'probability' as numeric(5, 2)) as probability,
    cast(payload->>'close_date' as date) as close_date,
    cast(payload->>'created_at' as timestamp) as created_at,
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
  and source_entity = 'opportunities'

select
    payload->>'lead_id' as lead_id,
    payload->>'campaign_id' as campaign_id,
    payload->>'company_name' as company_name,
    payload->>'email' as email,
    payload->>'country' as country,
    payload->>'lead_source' as lead_source,
    payload->>'status' as lead_status,
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
  and source_entity = 'leads'

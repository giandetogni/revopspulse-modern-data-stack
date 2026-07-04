select
    payload->>'campaign_id' as campaign_id,
    payload->>'campaign_name' as campaign_name,
    payload->>'channel' as channel,
    payload->>'target_segment' as target_segment,
    cast(payload->>'start_date' as date) as start_date,
    cast(payload->>'end_date' as date) as end_date,
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
  and source_entity = 'campaigns'

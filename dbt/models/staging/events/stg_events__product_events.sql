select
    payload->>'event_id' as event_id,
    payload->>'account_id' as account_id,
    payload->>'user_id' as user_id,
    payload->>'event_type' as event_type,
    cast(payload->>'event_timestamp' as timestamp) as event_timestamp,
    cast(payload->>'event_timestamp' as date) as event_date,
    payload->>'session_id' as session_id,
    payload->>'device_type' as device_type,
    payload->>'country' as country,
    payload->>'feature_name' as feature_name,
    nullif(payload->>'usage_count', '')::integer as usage_count,
    payload->>'report_type' as report_type,
    payload->>'prompt_location' as prompt_location,
    payload->>'cancellation_reason' as cancellation_reason,
    source_system,
    source_entity,
    source_table_or_endpoint,
    batch_id,
    extracted_at,
    load_date,
    raw_file_path,
    source_file_path,
    record_hash
from {{ source('raw_warehouse', 'json_records') }}
where source_system = 'product_events'
  and source_entity = 'product_events'

{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

select
    event_id,
    account_id,
    user_id,
    event_type,
    event_timestamp,
    event_date,
    session_id,
    device_type,
    country,
    feature_name,
    usage_count,
    report_type,
    prompt_location,
    cancellation_reason,
    source_system,
    source_entity,
    batch_id,
    extracted_at,
    load_date,
    raw_file_path,
    source_file_path,
    record_hash
from {{ ref('stg_events__product_events') }}

{% if is_incremental() %}
where event_timestamp > (
    select coalesce(max(event_timestamp), timestamp '1900-01-01')
    from {{ this }}
)
{% endif %}

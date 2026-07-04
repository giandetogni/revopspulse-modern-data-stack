with opportunities as (
    select * from {{ ref('stg_api__opportunities') }}
),

leads as (
    select * from {{ ref('stg_api__leads') }}
),

campaigns as (
    select * from {{ ref('stg_api__campaigns') }}
),

sales_reps as (
    select * from {{ ref('stg_postgres__sales_reps') }}
)

select
    opportunities.opportunity_id,
    opportunities.account_id,
    opportunities.lead_id,
    opportunities.campaign_id,
    opportunities.sales_rep_id,
    sales_reps.sales_rep_name,
    sales_reps.team as sales_team,
    sales_reps.region as sales_region,
    opportunities.opportunity_stage,
    opportunities.amount as opportunity_amount,
    opportunities.probability,
    opportunities.close_date,
    opportunities.created_at,
    opportunities.updated_at,
    leads.company_name as lead_company_name,
    leads.country as lead_country,
    leads.lead_source,
    leads.lead_status,
    campaigns.campaign_name,
    campaigns.channel as campaign_channel,
    campaigns.target_segment,
    case
        when opportunities.opportunity_stage = 'closed_won' then true
        else false
    end as is_closed_won,
    case
        when opportunities.opportunity_stage = 'closed_lost' then true
        else false
    end as is_closed_lost,
    opportunities.source_system,
    opportunities.batch_id,
    opportunities.extracted_at,
    opportunities.load_date,
    opportunities.raw_file_path,
    opportunities.record_hash
from opportunities
left join leads
    on opportunities.lead_id = leads.lead_id
left join campaigns
    on opportunities.campaign_id = campaigns.campaign_id
left join sales_reps
    on opportunities.sales_rep_id = sales_reps.sales_rep_id

with spend_monthly as (
    select
        date_trunc('month', spend_date)::date as metric_month,
        campaign_id,
        sum(amount) as marketing_spend
    from {{ ref('stg_api__marketing_spend') }}
    group by 1, 2
),

leads_monthly as (
    select
        date_trunc('month', created_at)::date as metric_month,
        campaign_id,
        count(distinct lead_id) as leads_count
    from {{ ref('stg_api__leads') }}
    group by 1, 2
),

opportunities_monthly as (
    select
        date_trunc('month', coalesce(close_date, created_at::date))::date as metric_month,
        campaign_id,
        count(distinct opportunity_id) as opportunities_count,
        count(distinct opportunity_id) filter (where is_closed_won) as closed_won_opportunities,
        sum(opportunity_amount) as pipeline_amount,
        sum(opportunity_amount) filter (where is_closed_won) as closed_won_revenue
    from {{ ref('fact_opportunities') }}
    group by 1, 2
),

campaign_months as (
    select metric_month, campaign_id from spend_monthly
    union
    select metric_month, campaign_id from leads_monthly
    union
    select metric_month, campaign_id from opportunities_monthly
),

final as (
    select
        cm.metric_month,
        cm.campaign_id,
        c.campaign_name,
        c.channel,
        c.target_segment,

        coalesce(s.marketing_spend, 0) as marketing_spend,
        coalesce(l.leads_count, 0) as leads_count,
        coalesce(o.opportunities_count, 0) as opportunities_count,
        coalesce(o.closed_won_opportunities, 0) as closed_won_opportunities,
        coalesce(o.pipeline_amount, 0) as pipeline_amount,
        coalesce(o.closed_won_revenue, 0) as closed_won_revenue,

        coalesce(
            round(
                coalesce(s.marketing_spend, 0)::numeric
                / nullif(l.leads_count, 0),
                4
            ),
            0
        ) as cost_per_lead,

        coalesce(
            round(
                coalesce(s.marketing_spend, 0)::numeric
                / nullif(o.closed_won_opportunities, 0),
                4
            ),
            0
        ) as cac,

        coalesce(
            round(
                coalesce(o.opportunities_count, 0)::numeric
                / nullif(l.leads_count, 0),
                4
            ),
            0
        ) as lead_to_opportunity_conversion_rate,

        coalesce(
            round(
                coalesce(o.closed_won_opportunities, 0)::numeric
                / nullif(l.leads_count, 0),
                4
            ),
            0
        ) as lead_to_closed_won_rate,

        coalesce(
            round(
                (
                    coalesce(o.closed_won_revenue, 0)
                    - coalesce(s.marketing_spend, 0)
                )::numeric
                / nullif(s.marketing_spend, 0),
                4
            ),
            0
        ) as marketing_roi,

        current_timestamp as created_at
    from campaign_months cm
    left join spend_monthly s
        on cm.metric_month = s.metric_month
        and cm.campaign_id = s.campaign_id
    left join leads_monthly l
        on cm.metric_month = l.metric_month
        and cm.campaign_id = l.campaign_id
    left join opportunities_monthly o
        on cm.metric_month = o.metric_month
        and cm.campaign_id = o.campaign_id
    left join {{ ref('stg_api__campaigns') }} c
        on cm.campaign_id = c.campaign_id
)

select *
from final

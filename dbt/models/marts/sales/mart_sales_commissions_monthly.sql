with payment_opportunity_candidates as (
    select
        p.payment_id,
        p.invoice_id,
        p.account_id,
        p.subscription_id,
        p.payment_date,
        p.payment_month,
        p.payment_status,
        p.invoice_status,
        p.payment_amount,
        p.refunded_amount,
        p.net_paid_amount,
        p.first_refund_date,
        p.is_successful_payment,
        p.has_refund,

        o.opportunity_id,
        o.sales_rep_id,
        o.sales_rep_name,
        o.sales_team,
        o.sales_region,
        o.opportunity_stage,
        o.opportunity_amount,
        o.close_date,
        o.is_closed_won,

        row_number() over (
            partition by p.payment_id
            order by
                o.is_closed_won desc nulls last,
                o.close_date desc nulls last,
                o.created_at desc nulls last
        ) as opportunity_rank
    from {{ ref('fact_payments') }} p
    left join {{ ref('fact_opportunities') }} o
        on p.account_id = o.account_id
),

payment_attribution as (
    select
        *,
        payment_status = 'succeeded'
            and invoice_status = 'paid'
            and coalesce(is_closed_won, false) = true
            as is_commission_eligible,

        has_refund = true
            and first_refund_date is not null
            and first_refund_date <= payment_date + interval '30 days'
            as has_30_day_clawback
    from payment_opportunity_candidates
    where opportunity_rank = 1
),

commission_events as (
    select
        payment_month as commission_month,
        sales_rep_id,

        count(*) as attributed_payments,
        count(*) filter (where is_commission_eligible) as eligible_payments,
        count(*) filter (where not is_commission_eligible) as ineligible_payments,

        sum(payment_amount) filter (where is_commission_eligible) as gross_paid_revenue,
        sum(refunded_amount) filter (where is_commission_eligible) as refunded_revenue,
        sum(net_paid_amount) filter (where is_commission_eligible) as commissionable_revenue,

        sum(refunded_amount) filter (
            where is_commission_eligible
              and has_30_day_clawback
        ) as clawback_revenue,

        sum(net_paid_amount * 0.05) filter (
            where is_commission_eligible
        ) as base_commission_amount,

        sum(refunded_amount * 0.05) filter (
            where is_commission_eligible
              and has_30_day_clawback
        ) as clawback_amount
    from payment_attribution
    where sales_rep_id is not null
    group by 1, 2
),

rep_months as (
    select
        target_month as commission_month,
        sales_rep_id
    from {{ ref('stg_postgres__sales_targets') }}

    union

    select
        commission_month,
        sales_rep_id
    from commission_events
),

final as (
    select
        rm.commission_month,
        rm.sales_rep_id,
        r.sales_rep_name,
        r.team as sales_team,
        r.region as sales_region,

        coalesce(t.target_revenue, 0) as target_revenue,
        coalesce(t.target_new_customers, 0) as target_new_customers,

        coalesce(e.attributed_payments, 0) as attributed_payments,
        coalesce(e.eligible_payments, 0) as eligible_payments,
        coalesce(e.ineligible_payments, 0) as ineligible_payments,

        coalesce(e.gross_paid_revenue, 0) as gross_paid_revenue,
        coalesce(e.refunded_revenue, 0) as refunded_revenue,
        coalesce(e.commissionable_revenue, 0) as commissionable_revenue,
        coalesce(e.clawback_revenue, 0) as clawback_revenue,

        coalesce(
            round(
                coalesce(e.commissionable_revenue, 0)::numeric
                / nullif(t.target_revenue, 0),
                4
            ),
            0
        ) as quota_attainment,

        case
            when coalesce(e.commissionable_revenue, 0) >= coalesce(t.target_revenue, 0)
                then greatest(
                    coalesce(e.commissionable_revenue, 0) - coalesce(t.target_revenue, 0),
                    0
                )
            else 0
        end as above_quota_revenue,

        coalesce(e.base_commission_amount, 0) as base_commission_amount,

        case
            when coalesce(e.commissionable_revenue, 0) >= coalesce(t.target_revenue, 0)
                then greatest(
                    coalesce(e.commissionable_revenue, 0) - coalesce(t.target_revenue, 0),
                    0
                ) * 0.08
            else 0
        end as accelerator_commission_amount,

        coalesce(e.clawback_amount, 0) as clawback_amount,

        greatest(
            coalesce(e.base_commission_amount, 0)
            + case
                when coalesce(e.commissionable_revenue, 0) >= coalesce(t.target_revenue, 0)
                    then greatest(
                        coalesce(e.commissionable_revenue, 0) - coalesce(t.target_revenue, 0),
                        0
                    ) * 0.08
                else 0
              end
            - coalesce(e.clawback_amount, 0),
            0
        ) as commission_payout,

        coalesce(
            round(
                coalesce(e.eligible_payments, 0)::numeric
                / nullif(e.attributed_payments, 0),
                4
            ),
            0
        ) as commission_accuracy_rate,

        current_timestamp as created_at
    from rep_months rm
    left join {{ ref('stg_postgres__sales_targets') }} t
        on rm.sales_rep_id = t.sales_rep_id
        and rm.commission_month = t.target_month
    left join commission_events e
        on rm.sales_rep_id = e.sales_rep_id
        and rm.commission_month = e.commission_month
    left join {{ ref('dim_sales_reps') }} r
        on rm.sales_rep_id = r.sales_rep_id
)

select *
from final

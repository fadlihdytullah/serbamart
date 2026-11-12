{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='sales_date') }}

with branch_days as (
    select
        branch_id,
        sales_date,
        count(distinct sale_id) as transactions,
        sum(revenue) as revenue
    from {{ ref('int_sales_lines') }}
    where channel = 'store'
    {% if is_incremental() %}
    and sales_date >= (select max(sales_date) - interval 7 days from {{ this }})
    {% endif %}
    group by branch_id, sales_date
),

with_average as (
    select
        *,
        cast(avg(revenue) over (
            partition by branch_id
            order by sales_date
            range between interval 7 days preceding and interval 1 day preceding
        ) as bigint) as avg_7_days
    from branch_days
)

select
    with_average.sales_date,
    with_average.branch_id,
    branches.name,
    branches.city,
    with_average.transactions,
    with_average.revenue,
    with_average.avg_7_days,
    round((with_average.revenue - with_average.avg_7_days) * 100.0 / with_average.avg_7_days, 1) as vs_avg_pct,
    rank() over (partition by with_average.sales_date order by with_average.revenue desc) as rank
from with_average
join {{ ref('stg_branches') }} as branches using (branch_id)
{% if is_incremental() %}
where with_average.sales_date >= (select max(sales_date) from {{ this }})
{% endif %}

with branches as (
    select sales_date, sum(transactions) as sales, sum(revenue) as revenue
    from {{ ref('mart_branch_daily_sales') }}
    group by sales_date
)

select branches.*, daily.sales as daily_sales, daily.revenue as daily_revenue
from branches
join {{ ref('mart_daily_sales') }} as daily using (sales_date)
where daily.channel = 'store'
  and (branches.sales <> daily.sales or branches.revenue <> daily.revenue)

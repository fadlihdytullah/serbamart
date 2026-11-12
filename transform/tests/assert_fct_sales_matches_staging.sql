with staging as (
    select sales_date as date_day, count(*) as staging_rows
    from {{ ref('stg_pos_sales') }}
    group by sales_date
),

facts as (
    select date_day, count(*) as fact_rows
    from {{ ref('fct_sales') }}
    where channel = 'store'
    group by date_day
)

select staging.date_day, staging.staging_rows, coalesce(facts.fact_rows, 0) as fact_rows
from staging
left join facts using (date_day)
where staging.staging_rows != coalesce(facts.fact_rows, 0)

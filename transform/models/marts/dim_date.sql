with bounds as (
    select min(sales_date) as first_day, max(sales_date) as last_day
    from {{ ref('int_sales_lines') }}
),

days as (
    select cast(range as date) as date_day
    from bounds, range(bounds.first_day, bounds.last_day + interval 1 day, interval 1 day)
)

select
    date_day,
    year(date_day) as year,
    month(date_day) as month,
    monthname(date_day) as month_name,
    strftime(date_day, '%Y-%m') as year_month,
    isodow(date_day) as day_of_week,
    dayname(date_day) as day_name,
    isodow(date_day) >= 6 as is_weekend
from days

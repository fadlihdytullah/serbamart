select
    sales_date,
    channel,
    count(distinct sale_id) as sales,
    sum(qty) as units,
    sum(revenue) as revenue
from {{ ref('int_sales_lines') }}
group by sales_date, channel

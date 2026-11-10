select
    lines.sales_date,
    lines.channel,
    lines.sku,
    products.name,
    products.category,
    sum(lines.qty) as units,
    sum(lines.revenue) as revenue
from {{ ref('int_sales_lines') }} as lines
join {{ ref('stg_products') }} as products using (sku)
group by all

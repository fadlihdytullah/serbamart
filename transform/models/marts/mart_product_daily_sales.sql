{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='sales_date') }}

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
{% if is_incremental() %}
where lines.sales_date >= (select max(sales_date) from {{ this }})
{% endif %}
group by all

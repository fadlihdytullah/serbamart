{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='date_day', on_schema_change='fail') }}

select
    sales.sale_id,
    sales.channel,
    sales.sales_date as date_day,
    coalesce(sales.branch_id, 'WEB') as branch_id,
    products.product_key,
    sales.sku,
    sales.qty,
    sales.unit_price,
    sales.revenue
from {{ ref('int_sales_lines') }} as sales
left join {{ ref('dim_product') }} as products
    on products.sku = sales.sku
    and sales.sales_date >= products.valid_from
    and sales.sales_date < products.valid_to
{% if is_incremental() %}
where sales.sales_date >= {{ incremental_since('date_day') }}
{% endif %}

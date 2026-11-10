select sales.*, products.unit_price as catalog_price
from {{ ref('fct_sales') }} as sales
join {{ ref('dim_product') }} as products using (product_key)
where sales.unit_price <> products.unit_price

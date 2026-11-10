select sales.*, products.unit_price as catalog_price
from {{ ref('stg_pos_sales') }} as sales
join {{ ref('stg_products') }} as products using (sku)
where sales.unit_price <> products.unit_price

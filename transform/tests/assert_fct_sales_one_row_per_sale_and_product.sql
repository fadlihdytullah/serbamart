select sale_id, sku, count(*) as rows
from {{ ref('fct_sales') }}
group by sale_id, sku
having count(*) > 1

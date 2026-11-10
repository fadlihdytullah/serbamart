select transaction_id, sku, count(*) as lines
from {{ ref('stg_pos_sales') }}
group by transaction_id, sku
having count(*) > 1

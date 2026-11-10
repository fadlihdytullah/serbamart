select *
from {{ ref('stg_pos_sales') }}
where qty <= 0 or unit_price <= 0

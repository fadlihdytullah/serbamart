{{ config(warn_if='>0', error_if='>100') }}

select sales.*
from {{ ref('stg_pos_sales') }} as sales
join {{ ref('stg_branches') }} as branches using (branch_id)
where hour(timezone(branches.timezone, sales.sold_at)) not between 7 and 22

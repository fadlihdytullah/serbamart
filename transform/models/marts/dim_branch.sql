select
    branch_id,
    name,
    city,
    timezone,
    opened_on,
    'store' as channel
from {{ ref('stg_branches') }}

union all

select
    'WEB' as branch_id,
    'Serbamart Online' as name,
    'Online' as city,
    null as timezone,
    null as opened_on,
    'online' as channel

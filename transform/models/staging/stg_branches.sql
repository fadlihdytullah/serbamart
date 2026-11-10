select
    branch_id,
    name,
    city,
    timezone,
    cast(opened_on as date) as opened_on
from {{ source('raw', 'branches') }}

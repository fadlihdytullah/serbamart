select city, count(*) as branches, min(opened_on) as first_opened
from {{ ref('branches') }}
group by city
order by branches desc, city

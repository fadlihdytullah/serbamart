{% test volume_vs_same_weekday(model, column_name, min_ratio=0.9, weeks=4) %}

with daily as (
    select {{ column_name }} as day, count(*) as row_count
    from {{ model }}
    group by 1
),

latest as (
    select * from daily
    order by day desc
    limit 1
),

usual as (
    select avg(daily.row_count) as row_count
    from daily, latest
    where daily.day in (
        select cast(latest.day - to_weeks(weeks.n) as date)
        from range(1, {{ weeks }} + 1) as weeks(n)
    )
)

select
    latest.day,
    latest.row_count,
    round(usual.row_count) as usual_row_count,
    round(latest.row_count / usual.row_count, 2) as ratio
from latest, usual
where latest.row_count < usual.row_count * {{ min_ratio }}

{% endtest %}

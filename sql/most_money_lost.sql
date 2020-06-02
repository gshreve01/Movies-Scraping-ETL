-- revenue vs budget comparison
select title, revenue - budget [money_made]
from movie
order by money_made
limit 10
select m.title, m.revenue, m.popularity
from movie m
order by m.revenue DESC
limit 25

-- revenue vs budget comparison
select title, revenue - budget [money_made]
from movie m
--join movie_genres mg on m.movie_id = mg.movie_id
--join genres g on mg.genres_id = g.genres_id
--where g.geners_name = 'Horror'
order by money_made DESC
limit 10
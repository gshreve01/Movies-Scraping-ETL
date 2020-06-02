select m.title, g.geners_name
from movie m
join movie_genres mg on m.movie_id = mg.movie_id
join genres g on mg.genres_id = g.genres_id
order by m.title

select m.title, m.release_date, m.popularity, t1.avg_rating, am.rating [Amazon rating], am.amazon_link
from movie m
join (select  movie_id, avg(rating) [avg_rating]
from rating
group by movie_id
) t1 on m.movie_id = t1.movie_id
left join amazon_movie am on am.movie_id = m.movie_id
order by avg_rating desc, m.title
limit 25

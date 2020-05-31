import pandas as pd
import datetime as dt
import os
import json

create_genres_path = os.path.dirname(__file__)

def load_clean_movie_file():
    #import the movies csv file into dataframe
    file_movie = f"{create_genres_path}/../files/movies_clean_1.csv"

    #columns to import from csv file .. 
    col_list = ["id", "genres" ]
    movies_df = pd.read_csv(file_movie,usecols=col_list, low_memory=False)
    print (f"Orinal record count: {len(movies_df)}")
    movies_df.head(5)
    return movies_df

def generate_generas_dfs(movies_df):
    genres_list = []
    movies_genres_list = []
    for index, movie in movies_df.iterrows():
        genres_json = movie.genres.replace("'", "\"")
        genres = json.loads(genres_json)
        for genre in genres:
            if not genre in genres_list:
                genres_list.append(genre)
            movie_genre = {"movie_id": str(movie.id), "genre_id": str(genre["id"])}
            movies_genres_list.append(movie_genre)
    return pd.DataFrame(genres_list), pd.DataFrame(movies_genres_list)

def save_data(genres_df, movies_genres_df):
    genres_file = f"{create_genres_path}/../files/genres.csv"
    genres_df.to_csv(genres_file, index=False)

    movies_genres_file = f"{create_genres_path}/../files/movies_genres.csv"
    movies_genres_df.to_csv(movies_genres_file, index=False)

    

movies_df = load_clean_movie_file()
genres_df, movies_genres_df = generate_generas_dfs(movies_df)
print(genres_df.head(20))
print(movies_genres_df.head())
save_data(genres_df, movies_genres_df)
print("genres csv data file generation complete")
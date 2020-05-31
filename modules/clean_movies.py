import pandas as pd
import datetime as dt
import os

clean_movies_path = os.path.dirname(__file__)

def load_movies_meta():
    #import the movies csv file into dataframe
    file_movie = f"{clean_movies_path}/../files/movies_metadata.csv"

    #columns to import from csv file .. 
    col_list = ["adult", "budget", "id", "imdb_id", "original_language", "title", "release_date", "revenue", "runtime", "status", "vote_average", "vote_count", "original_title", "popularity", "genres", "production_companies" ]
    movies_df = pd.read_csv(file_movie,usecols=col_list, low_memory=False)
    print (f"Orinal record count: {len(movies_df)}")
    movies_df.head(5)
    return movies_df

def clean_remove_budget(movies_df):
    movies_df["budget"] = movies_df["budget"].astype(str) 
    movies_df = movies_df[movies_df.budget.apply(lambda x: x.isnumeric())]
    movies_df["budget"] = movies_df["budget"].astype(int)
    movies_df = movies_df.loc[movies_df["budget"] > 0]
    print (f"Record count after budget 0 removed: {len(movies_df)}")
    movies_df.head(5)
    return movies_df

def clean_data(movies_df):
    #remove duplicate id from dataframe
    movies_df.drop_duplicates(subset='id', inplace=True)

    #convert id to int and remove the non-numeric ids
    movies_df[["id"]] = movies_df[["id"]].apply(pd.to_numeric, errors='coerce')

    # #remove null or na
    movies_df.dropna(subset=['id'], inplace= True)

    print(f"Record count after data cleanup: {len(movies_df)}")

    return movies_df


def save_data(movies_df):
    clean_file = f"{clean_movies_path}/../files/movies_clean_1.csv"
    movies_df.to_csv(clean_file)

movies_df = load_movies_meta()
movies_df = clean_remove_budget(movies_df)
movies_df = clean_data(movies_df)
save_data(movies_df)

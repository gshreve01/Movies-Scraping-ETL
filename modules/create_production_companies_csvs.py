import pandas as pd
import datetime as dt
import os
import json

create_productioncompanies_path = os.path.dirname(__file__)

def load_clean_movie_file():
    #import the movies csv file into dataframe
    file_movie = f"{create_productioncompanies_path}/../files/movies_clean_1.csv"

    #columns to import from csv file .. 
    col_list = ["id", "production_companies" ]
    movies_df = pd.read_csv(file_movie,usecols=col_list, low_memory=False)
    print (f"Orinal record count: {len(movies_df)}")
    print(movies_df.head(5))
    return movies_df

def generate_production_companies_dfs(movies_df):
    productioncompanies_list = []
    movies_productioncompanies_list = []
    for index, movie in movies_df.iterrows():
        #json_dictionaries = json.loads(movie.production_companies)
        splits = movie.production_companies.split("{")
        for idx in range(1, len(splits)):
            # the name value is from the colon to the , "id":
            production_company_line = splits[idx]
            find_idx = production_company_line.find(", 'id':", 9)
            name_value = production_company_line[9:find_idx-1]
            production_company_line = production_company_line[find_idx + 8: len(production_company_line)]
            find_idx = production_company_line.find("}")
            id_value = production_company_line[0:find_idx]
            production_company = {"name": name_value, "id": str(id_value)}
            if not production_company in productioncompanies_list:
                productioncompanies_list.append(production_company)
            movie_genre = {"movie_id": str(movie.id), "production_company_id": id_value}
            movies_productioncompanies_list.append(movie_genre)
    return pd.DataFrame(productioncompanies_list), pd.DataFrame(movies_productioncompanies_list)

def save_data(production_companies_df, movies_production_companies_df):
    production_compoanies_file = f"{create_productioncompanies_path}/../files/production_companies.csv"
    production_companies_df.to_csv(production_compoanies_file, index=False)

    movies_production_companies_file = f"{create_productioncompanies_path}/../files/movies_productioncompanies.csv"
    movies_production_companies_df.to_csv(movies_production_companies_file, index=False)

    

movies_df = load_clean_movie_file()
production_companies_df, movies_production_companies_df = generate_production_companies_dfs(movies_df)
print(production_companies_df.head(20))
print(movies_production_companies_df.head())
save_data(production_companies_df, movies_production_companies_df)
print("production companies csv data file generation complete")
import pandas as pd
import os
from splinter import Browser
from bs4 import BeautifulSoup
import urllib.parse
from io import StringIO
import time
import datetime


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    path = os.path.dirname(__file__)
    executable_path = {'executable_path': f'{path}/chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def load_movies_into_df():
    # Running it outside of debug mode, the path is not setting correctly
    path = os.path.dirname(__file__)
    movies_csv = f"{path}/../files/movies_clean_1.csv"
    movies_df = pd.read_csv(movies_csv)[["id", "title", "original_title", "release_date", "budget"]]

    return movies_df

def find_movie(browser, movie_id, title, original_title, release_date):
    url_base = "https://www.amazon.com/s?k=dvd+movie+{escape_movie}+{year}&ref=nb_sb_noss"

    format_str = '%m/%d/%Y' # The format
    release_date = datetime.datetime.strptime(release_date, format_str)
    year = f"{release_date.year}"
    quoted_title = f'"{title}"'
    url = url_base.replace("{escape_movie}", urllib.parse.quote_plus(quoted_title))
    url = url.replace("{year}", year)
    print(url)

    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    search_result = soup.find_all("span", {"data-cel-widget": "MAIN-SEARCH_RESULTS"})

    accepted_classes = ["sg-col-inner", "s-include-content-margin"]
    found_movie = False
    for accepted_class in accepted_classes:
        result_items = search_result.find_all("div", class_=accepted_class)

        for movie_info in result_items:
            try:
                text = movie_info.text
                idx = text.find(title)
                if idx <= 0:
                    continue
               
                movie_name, rating = get_amazon_movie_name_ratings(movie_info, title, original_title, year)
                if rating != None:
                    found_movie = True
                    break

            except Exception:
                print("oops....not the section we are looking for")

        if (found_movie):
            break

    if found_movie:
        return {"movie_id": movie_id
                , "amazon_title": movie_name
                , "rating": rating
                , "amazon_link": f"www.amazon.com{link}"
        }
    return None

def get_amazon_movie_name_ratings(movie_info, title, original_title, year):
    h2 = movie_info.find("h2")
    anchor = h2.find("a")
    span = anchor.find("span")
    movie_name = span.get_text()

    # need to find colon and only take movie name to that point
    compare_movie_name = movie_name.rpartition(':')[0]
    bfound = False
    if (compare_movie_name == title or compare_movie_name == original_title):
        if (movie_name != compare_movie_name):
            if does_release_year_match(h2, year):
                bfound = True
        else:
            bfound = True
    if bfound:
        link = anchor.attrs["href"]
        print(link)
        rating = get_rating(movie_info)
    else:
        rating = None

    return movie_name, rating

def does_release_year_match(h2, movie_release_year):
    year_div = h2.next_sibling.next_sibling
    span = year_div.find_("span")
    amazon_release_year = span.get_text()
    return amazon_release_year == movie_release_year


def get_rating(movie_info):
    spans = movie_info.find_all("span")
    for span in spans:
        if span.has_attr("aria-label"):
            attr = span.attrs["aria-label"]
            if attr != None:
                rating = attr
                return rating
    return None
    

movies_df = load_movies_into_df()
browser = init_browser()
print(movies_df.head())

movies = []
for index, movie in movies_df.head(2).iterrows():
    print(movie)
    movie = find_movie(browser, movie.id, movie.title, movie.original_title, movie.release_date)
    if movie != None:
        movies.append(movie)

print(movies)
browser.quit()

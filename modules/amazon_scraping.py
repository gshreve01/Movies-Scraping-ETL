import pandas as pd
import os
from splinter import Browser
from bs4 import BeautifulSoup
import urllib.parse
from io import StringIO
import time
import datetime
import sys, traceback

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
    url_base = "https://www.amazon.com/s?k=dvd+movie+{escape_movie}&ref=nb_sb_noss"
    quoted_title = f'"{title}"'
    url = url_base.replace("{escape_movie}", urllib.parse.quote_plus(quoted_title))
    found_movie = find_movie_with_url(browser, url, movie_id, title, original_title, release_date, None)

    if found_movie == None and release_date != None:
        url_base = "https://www.amazon.com/s?k=dvd+movie+{escape_movie}+{year}&ref=nb_sb_noss"
        format_str = '%m/%d/%Y' # The format
        release_date = datetime.datetime.strptime(release_date, format_str)
        year = f"{release_date.year}"
        quoted_title = f'"{title}"'
        url = url_base.replace("{escape_movie}", urllib.parse.quote_plus(quoted_title))
        url = url.replace("{year}", year)
        found_movie = find_movie_with_url(browser, url, movie_id, title, original_title, release_date, year)

    return found_movie

def find_movie_with_url(browser, url, movie_id, title, original_title, release_date, year):
    print(url)
    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find_all("span", {"data-cel-widget": "MAIN-SEARCH_RESULTS"})

    found_movie = None
    for search_result in search_results:
        found_movie = process_search_result(search_result, movie_id, title, original_title, release_date, year)
        if found_movie:
            break

    return found_movie


def process_search_result(search_result, movie_id, title, original_title, release_date, year):
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
               
                movie_name, rating, link = get_amazon_movie_name_ratings(movie_info, title, original_title, year)
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
    
    amazon_movie_name = movie_name = span.get_text()
    movie_name = amazon_movie_name.lower()

    # need to find colon and only take movie name to that point
    movie_name_possibilities = []
    movie_name_possibilities.append(movie_name)
    movie_name_possibilities.append(movie_name.rpartition(':')[0])

    bfound = False
    link = None
    for compare_movie_name in  movie_name_possibilities:
        if (compare_movie_name == title.lower() or compare_movie_name == original_title.lower()):
            if (movie_name != compare_movie_name):
                if does_release_year_match(h2, year):
                    bfound = True
                    break
            else:
                bfound = True
                break
    if bfound:
        link = anchor.attrs["href"]
        rating = get_rating(movie_info)
    else:
        rating = None

    return amazon_movie_name, rating, link

def does_release_year_match(h2, movie_release_year):
    year_div = h2.next_sibling.next_sibling
    span = year_div.find("span")
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
    
def save_amazon_data(movies, not_found_movies):
    path = os.path.dirname(__file__)
    amazon_csv = f"{path}/../files/amazon_ratings.csv"
    df = pd.DataFrame(movies)
    df.to_csv(amazon_csv, index=False)

    df = pd.DataFrame(not_found_movies)
    not_found_csv = f"{path}/../files/amazon_ratings_not_found.csv"
    df.to_csv(not_found_csv, index=False)

def is_date(date_obj):
    is_date = True
    try:
        format_str = '%m/%d/%Y' # The format
        date = datetime.datetime.strptime(date_obj, format_str)
    except Exception as e:
        is_date = False
        print(e)
    return is_date

movies_df = load_movies_into_df()
browser = init_browser()
print(movies_df.head())

movies = []
not_found_movies = []
try:
    count = 0
    skipRows = True
    for index, movie in movies_df.iterrows():
        count += 1
        print(f"[{movie.title}] - {count}")
        # if count > 10:
        #     break

        if movie.title == "Dreamkiller":
            skipRows = False

        if skipRows:
            continue

        # should have been part of cleaning data process
        release_date = movie.release_date
        if not is_date(release_date):
            release_date = None
        amazon_movie = find_movie(browser, movie.id, movie.title, movie.original_title, release_date)
        if amazon_movie != None:
            print(amazon_movie)
            movies.append(amazon_movie)
        else:
            not_found_movies.append(movie)
            print("did not find movie", movie)
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("*** print_tb:")
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print("*** print_exception:")
    # exc_type below is ignored on 3.5 and later
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
    print("*** print_exc:")
    traceback.print_exc(limit=2, file=sys.stdout)
    print("*** format_exc, first and last line:")
    formatted_lines = traceback.format_exc().splitlines()
    print(formatted_lines[0])
    print(formatted_lines[-1])
    print("*** format_exception:")
    # exc_type below is ignored on 3.5 and later
    print(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
    print("*** extract_tb:")
    print(repr(traceback.extract_tb(exc_traceback)))
    print("*** format_tb:")
    print(repr(traceback.format_tb(exc_traceback)))
    print("*** tb_lineno:", exc_traceback.tb_lineno)

    print("Failed....save what you can")
    print(e)
save_amazon_data(movies, not_found_movies)

browser.quit()

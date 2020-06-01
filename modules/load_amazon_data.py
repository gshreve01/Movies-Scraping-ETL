import pandas as pd
import datetime as dt
import os

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, null, ForeignKey, MetaData, Table
from sqlalchemy.orm import Session
Base = declarative_base()

create_files_path = os.path.dirname(__file__)


# Path to sqlite
database_path = f"{create_files_path}/../database/combined_data.sqlite"

# Create an engine that can talk to the database
engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()
session = Session(bind=engine)

# Create tables, classes and databases
# ----------------------------------
try:
    meta = MetaData()
    amazon_movie = Table(
        'amazon_movie', meta, 
        Column('movie_id', Integer, ForeignKey("movie.movie_id"), primary_key=True, autoincrement=False),
        Column('amazon_title', String(500), nullable=False),
        Column('rating', String(20), nullable=True),
        Column('amazon_link', String(500), nullable=True),
    )
    
    meta.create_all(engine)
except Exception as e:
    print(e)
    print("the table already exists")

class Movie(Base):
    __tablename__ = 'movie'
    movie_id = Column(Integer, primary_key=True, autoincrement=False)
    adult = Column(String(10), nullable=True)
    budget = Column(Float, nullable=True)
    imdb_id = Column(String(40), nullable=True)
    language = Column(String(10), nullable=True)
    title = Column(String(512), nullable=True)
    popularity = Column(Float, nullable=True)
    release_date = Column(Date, nullable=True)
    revenue = Column(Float, nullable=True)
    runtime = Column(Float, nullable=True)
    status = Column(String(10), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Float, nullable=True)

class AmazonMovie(Base):
    __tablename__ = "amazon_movie"
    movie_id = Column(Integer, ForeignKey("movie.movie_id"), primary_key=True, autoincrement=False)
    amazon_title = Column(String(500), nullable=False)
    rating = Column(String(20), nullable=True)
    amazon_link = Column(String(500), nullable=True)


def process_file(csv_file_name):
    print(f"Processing file: {csv_file_name}")
    movies_df = pd.read_csv(file_movie, low_memory=False)
    for index, row in movies_df.iterrows():
        amazon_movie = AmazonMovie(movie_id = row["movie_id"], amazon_title=row["amazon_title"], rating=row["rating"], amazon_link=row["amazon_link"])
        session.add(amazon_movie)

    session.commit()

# start import of data process
print("Starting process of Amazon Data Injestion")

print("Delete existing data")
try:
    conn.execute("delete from amazon_movie")
except Exception as e:
    print(e)
    print("No records to delete")

file_movie = f"{create_files_path}/../files/amazon_ratings.1.csv"
process_file(file_movie)

file_movie = f"{create_files_path}/../files/amazon_ratings.2.csv"
process_file(file_movie)





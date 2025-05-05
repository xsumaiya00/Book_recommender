from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI()

# Load the data
books = pd.read_csv("Books.csv", encoding='latin-1')
ratings = pd.read_csv("Ratings.csv", encoding='latin-1')

# Clean column names
books.columns = books.columns.str.strip()
ratings.columns = ratings.columns.str.strip()

# Merge ratings with book metadata
book_ratings = pd.merge(ratings, books, on='ISBN')


# Define recommendation logic
def recommend_books_for_fans_of(title="lord of the rings", min_rating=8, top_n=10):
    fans = book_ratings[
        book_ratings['Book-Title'].str.contains(title, case=False, na=False) &
        (book_ratings['Book-Rating'] >= min_rating)
    ]
    fan_user_ids = fans['User-ID'].unique()

    other_books = book_ratings[
        (book_ratings['User-ID'].isin(fan_user_ids)) &
        (book_ratings['Book-Rating'] >= min_rating)
    ]
    filtered = other_books[~other_books['Book-Title'].str.contains(title, case=False, na=False)]

    top_books = (
        filtered.groupby('Book-Title')
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index(name='score')
    )

    return top_books


# FastAPI root route
@app.get("/")
def read_root():
    return {"message": "Book Recommender API is running."}


# Recommender endpoint
@app.get("/recommend")
def get_recommendations(title: str = Query(..., description="Book title to base recommendations on")):
    try:
        results = recommend_books_for_fans_of(title)
        return results.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

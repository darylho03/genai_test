import psycopg2
import random
import ollama
import os

conn = psycopg2.connect(dbname="mydb", user="darylho", password=os.getenv("DATABASE_PASSWORD"),)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS store (
        product TEXT,
        orders INTEGER,
        stock INTEGER
    );
""")

# Clear the store table before inserting new data
cur.execute("DELETE FROM store;")

cur.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        title TEXT,
        rating REAL,
        views INTEGER,
        gross INTEGER
    );
""")

# Clear the movies table before inserting new data
cur.execute("DELETE FROM movies;")

# Generate random data for the table
# 100 random grocery items as a comma-separated Python list
grocery_items = [
    "Apple", "Banana", "Orange", "Milk", "Bread", "Eggs", "Cheese", "Butter", "Yogurt", "Chicken",
    "Beef", "Pork", "Fish", "Shrimp", "Rice", "Pasta", "Flour", "Sugar", "Salt", "Pepper",
    "Tomato", "Lettuce", "Spinach", "Carrot", "Broccoli", "Cauliflower", "Potato", "Onion", "Garlic", "Cucumber",
    "Celery", "Bell Pepper", "Mushroom", "Corn", "Peas", "Green Beans", "Zucchini", "Eggplant", "Avocado", "Lime",
    "Lemon", "Grapes", "Strawberry", "Blueberry", "Raspberry", "Watermelon", "Pineapple", "Mango", "Peach", "Plum",
    "Cherry", "Pear", "Kiwi", "Cantaloupe", "Honeydew", "Pumpkin", "Squash", "Radish", "Turnip", "Beet",
    "Cabbage", "Brussels Sprouts", "Asparagus", "Artichoke", "Okra", "Chili Pepper", "Jalapeno", "Basil", "Parsley", "Cilantro",
    "Rosemary", "Thyme", "Oregano", "Sage", "Dill", "Mint", "Chives", "Almonds", "Walnuts", "Peanuts",
    "Cashews", "Hazelnuts", "Sunflower Seeds", "Pumpkin Seeds", "Raisins", "Dates", "Figs", "Cranberries", "Coconut", "Tofu",
    "Tempeh", "Soy Milk", "Oat Milk", "Almond Milk", "Maple Syrup", "Honey", "Jam", "Jelly", "Mustard", "Ketchup"
]

for i in range(100):
    product = grocery_items[i % len(grocery_items)]
    stock = random.randint(1, 100)  # Example stock quantity, decreasing with each item
    orders = random.randint(1, stock)  # Random number of orders between 1 and 100
    
    cur.execute(
        "INSERT INTO store (product, orders, stock) VALUES (%s, %s, %s);",
        (product, orders, stock)
    )

movie_names = [
    "Inception", "The Matrix", "Interstellar", "The Godfather", "Pulp Fiction",
    "The Dark Knight", "Forrest Gump", "Fight Club", "The Shawshank Redemption", "Gladiator",
    "The Lord of the Rings", "Star Wars", "Jurassic Park", "Titanic", "Avatar",
    "The Silence of the Lambs", "Schindler's List", "Saving Private Ryan", "The Departed", "Goodfellas",
    "The Social Network", "The Big Lebowski", "Back to the Future", "The Avengers",
    "Spider-Man", "Guardians of the Galaxy", "Wonder Woman", "Black Panther", "The Incredibles"
]

for i in range(len(movie_names)):
    movie = movie_names[i % len(movie_names)]
    rating = random.uniform(1.0, 5.0)  # Random rating between 1.0 and 5.0
    views = random.randint(1000, 100000)  # Random views between 1000 and 100000
    gross = random.randint(1000000, 100000000)  # Random gross earnings between 1M and 100M

    cur.execute(
        "INSERT INTO movies (title, rating, views, gross) VALUES (%s, %s, %s, %s);",
        (movie, rating, views, gross)
    )

conn.commit()
cur.close()
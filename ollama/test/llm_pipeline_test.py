import psycopg2
import random
import ollama

conn = psycopg2.connect(dbname="mydb", user="darylho", password="Mountainlake15")
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

conn.commit()
cur.close()

system_prompt = "You are an LLM to SQL translator that converts user questions into SQL queries. The database is a grocery store with a table named 'store' that has the following columns: product (TEXT), orders (INTEGER), and stock (INTEGER). The user will ask questions about the grocery store, and you will provide the SQL query that another LLM can use to answer the question. The SQL query should be valid and executable on the 'store' table. You will not provide any explanations or additional information, nor will you edit your first query or add any revisions in your response, only the SQL query itself in the format ```<SQL_QUERY>``` without any additional text or formatting. For example, for the question: 'What are the 5 items with the highest stock?', you would respond with '''SELECT product FROM store ORDER BY stock DESC LIMIT 5;'''. DO NOT ADD ANYTHING ELSE AFTER THE QUERY, start the response with triple single quotes and end the response with triple single quotes. If there are any direct mentions of item names, you will reformat the item name so that the first letter is capitalized and the rest are lowercase, e.g., 'apples' becomes 'Apple', 'BANANAS' becomes 'Banana', 'hazelnut' becomes 'Hazelnuts'. If the question is not answerable with a SQL query, you will respond with '''No valid SQL query found.'''. If the question is asking for a lot of data at once, limit the amount of data returned to a maximum of 10 rows."

user_prompt = input("Please enter your question: ")

response = ollama.chat(
    model='llama3.2:latest',
    messages=[
        {
            'role': 'system',
            'content': system_prompt,
        },
        {
            'role': 'user',
            'content': user_prompt,
        },
    ],
)
interaction = {
    'model': 'llama3.2:latest',
    'prompt': user_prompt,
    'response': response['message']['content'],
}
print("Generated SQL Query:")
query = response['message']['content']
# Clean up the query by removing any leading/trailing whitespace and 'sql' prefix if present
if query.startswith("```") or query.startswith("'''"):
    query = query[3:]
if query.endswith("```") or query.endswith("'''"):
    query = query[:-3]
if query.startswith("sql") or query.startswith("SQL"):
    query = query[3:]
print(query)

with conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    print("Query Results:")
    print(rows)

new_system_prompt = f"""You are the back part of an LLM to SQL translator. You are responsible for taking in the result of the SQL query and providing a response to the user based on the results. The initial user question was: '{user_prompt}'. The SQL query generated was: '{query}'. The results of the SQL query are: {rows}. Based on these results, please provide a concise and relevant answer to the user's question. Answer as if you were answering the original user's question and do not mention the SQL query or the results directly. Do not provide any explanations or additional information, only the final answer to the user's question. If the question is not answerable with the provided data, respond with 'No relevant data found.'"""

response = ollama.chat(
    model='llama3.2:latest',
    messages=[
        {
            'role': 'user',
            'content': new_system_prompt,
        },
    ],
)

print("Final Response:")
print(response['message']['content'])
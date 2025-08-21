import json
import os
from flask import Flask, jsonify, request
import ollama
import pdfplumber
from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg2.connect(
    dbname="mydb",
    user="darylho",
    password=os.getenv("DATABASE_PASSWORD"),
    host="localhost",
    port=5432
    
)
register_vector(conn)

system_prompts = {
    'Icely Puzzles': 'You are a puzzle game content creator named IcelyPuzzles. You create content showcasing or playthroughs of popular or niche puzzle games. You also have an obsession with Chess Evolved Online, an online chess variant with custom pieces. You also have an inside joke on your channel called "Chess Battle Advaced", a game based on Chess Evolved Online also with custom pieces, but is mainly a meme to you because of its ridiculous title screen music. No matter what, you must reference Chess Battle Advanced or CBA (the abbreviation) at least once in every response. If it is ever relevant in responses, your favorite puzzle games are "Baba is You", "Lingo", and "Patrick\'s Parabox". You also don\'t typically create a narrative in your commentary and stray closer to the technical side of the game, such as game design decisions, strategies, tactics, and mechanics. For example, when you cover a game you\'re playing for the first time, you immediately point out any bugs or odd game design decisions you see and joke about them (usually just saying Chess Battle Advanced in the presence of one of them). You also have a very dry sense of humor, and you often make sarcastic comments about the games you play. You are also very critical of games that you find to be poorly designed or unbalanced, and you are not afraid to express your opinions on them. You also highly praise good puzzle design, as a puzzle game enthusiast and former puzzle game playtester, you have a keen eye for what makes a good puzzle game. You also have a very analytical mind, and you often break down games into their individual components to analyze them. You also have a very strong sense of aesthetics, and you often comment on the visual design of the games you play. The following is an example of an intro to a video you would make of a niche puzzle game that just released called "Threadbound": "Welcome to a game called Threadbound, which is a puzzle platformer all about writing your own laws of physics, and from what I heard from Steam reviews, this is incredible. There is around 2-3 hours of gameplay in this demo, starts kinda slow but oh my god. Its so polished and good already. Like I don\'t normally say "must play" but that is a good... really fitting label for this game. Let\'s get into the gameplay now. Also this is not sponsored."',
    'Balatro University': 'You are a Balatro content creator named Balatro University. You mainly create content on Balatro, a roguelike deckbuilding game where you play poker hands to reach higher and higher scores. You are one of the best, if not the best, Balatro player in the world, and you are known for your high scores and your ability to play the game at a high level. Your content is also very informative and you explain every play you make in great detail, explaining why you make every play and why you don\'t make some others. Your analytical and strategic mind comes from your background with having a PhD in Mathematics and being a former math professor. Your main words/phrases that are iconic to your YouTube channel and Twitch livestream are "muhnee", used to replace the word "money" at times when your current emphasis in Balatro is building economy, "go next", used when you exit the shop in Balatro.',
    'NairoMK': 'You are a content creator named NairoMK, or Nairo for short, but mainly referred to as NairoMK. You mainly create content on Super Smash Bros. Ultimate and Mario Kart, but rarely play variety. You are a very competitive player, but also a very good player, and a former professional player in Super Smash Bros. Ultimate at tournaments, but due to unfortunate circumstanses you will never bring up ever, you now only create content for it online. Your main personality is sarcastically cocky/arrogant and will often trashtalk your opponents or members of chat in a humorous manner. Your main common words/phrases that are iconic to your YouTube channel and YouTube livestream are "YOU KNOW THE VIBES!", used as an intro for videos or when destroying opponents in smash, "KICKED IN YO CHEST!", used when your character in smash uses a move that kicks an opponent, "YA LOST!", used when you believe you or someone you are watching is about to destroy an opponent, "Your gem is crushed/eviscerated", used when you ban a user in chat or used when blocking a user on smash ultimate, typically for lagging, "MID!", when particular characters appear on screen or are mentioned, those characters being Sephiroth, Cloud, and Palutena (your main at past tournaments). You also have a tendency of bringing up Sephiroth in the most seemingly random points in your videos, due to your disappointment in how weak the character is in smash, often bringing him up to compare him to other characters in the game, such as "Sephiroth would have died from that" or "Another character better than Sephiroth", often reffering to him as "MID". When responding to prompts, be sure to FULLY CAPITALIZE some words, such as "YOU KNOW THE VIBES!" or "KICKED IN YO CHEST!" to simulate that you are yelling them and emphasizing them. For example, here is what an intro to a video you would make of a Super Smash Bros. Ultimate tournament reaction video would look like: "YOUTUBE! YOU KNOW THE VIBES! Today we are going to be reacting to Kagaribi 13, the largest Smash Ultimate tournament in HISTORY, hosted in Japan! Today, we will be watching pools, hopefully seeing some of our predictions some true, and hopefully seeing AMERICA pull through. That means YOU "LIGHT", if I see you lose to Miya\'s game & watch when I literally TRAINED you last week, your gem is eviscerated. But anyway, let\'s start watching some matches."',
}

@app.route('/chatbot/<name>', methods=['POST'])
def get_response(name):
    print(request)
    data = request.get_json()
    print("Received request:", data)
    prompt = data.get("prompt", "")
    print("Prompt received:", prompt)
    assistant_response = ollama.chat(
        model='llama3.2:latest',
        messages=[
            {
                'role': 'system',
                'content': system_prompts[name]
            },
            {
                'role': 'user',
                'content': prompt
            },
        ],
    )
    return jsonify({"response": assistant_response['message']['content']})

@app.route('/chatbot/custom', methods=['POST'])
def get_custom_response():
    data = request.get_json()
    system_prompt = data.get("system_prompt", "")
    user_prompt = data.get("user_prompt", "")
    
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
    return jsonify({"response": response['message']['content']})

@app.route('/sql', methods=['POST'])
def sql_query():
    sql_prompts = {
        "Store": "You are an LLM to SQL translator that converts user questions into SQL queries. The database is a grocery store with a table named 'store' that has the following columns: product (TEXT), orders (INTEGER), and stock (INTEGER). The user will ask questions about the grocery store, and you will provide the SQL query that another LLM can use to answer the question. The SQL query should be valid and executable on the 'store' table. You will not provide any explanations or additional information, nor will you edit your first query or add any revisions in your response, only the SQL query itself in the format ```<SQL_QUERY>``` without any additional text or formatting. For example, for the question: 'What are the 5 items with the highest stock?', you would respond with '''SELECT product FROM store ORDER BY stock DESC LIMIT 5;'''. DO NOT ADD ANYTHING ELSE AFTER THE QUERY, start the response with triple single quotes and end the response with triple single quotes. If there are any direct mentions of item names, you will reformat the item name so that the first letter is capitalized and the rest are lowercase, e.g., 'apples' becomes 'Apple', 'BANANAS' becomes 'Banana', 'hazelnut' becomes 'Hazelnuts'. If the question is not answerable with a SQL query, you will respond with '''No valid SQL query found.'''. If the question is asking for a lot of data at once, limit the amount of data returned to a maximum of 10 rows.",
        "Movies": "You are an LLM to SQL translator that converts user questions into SQL queries. The database is a movie database with a table named 'movies' that has the following columns: title (TEXT), rating (REAL), views (INTEGER), and gross (INTEGER). The user will ask questions about movies, and you will provide the SQL query that another LLM can use to answer the question. The SQL query should be valid and executable on the 'movies' table. You will not provide any explanations or additional information, nor will you edit your first query or add any revisions in your response, only the SQL query itself in the format ```<SQL_QUERY>``` without any additional text or formatting. For example, for the question: 'What are the 5 highest rated movies?', you would respond with '''SELECT title FROM movies ORDER BY rating DESC LIMIT 5;'''. DO NOT ADD ANYTHING ELSE AFTER THE QUERY, start the response with triple single quotes and end the response with triple single quotes. If there are any direct mentions of movie titles, you will reformat the title so that the first letter is capitalized and the rest are lowercase, e.g., 'inception' becomes 'Inception', 'the matrix' becomes 'The Matrix'. If the question is not answerable with a SQL query, you will respond with '''No valid SQL query found.'''. If the question is asking for a lot of data at once, limit the amount of data returned to a maximum of 10 rows."
    }
    user_prompt = request.json.get('prompt', '')
    determined_prompt = ollama.chat(
        model='llama3.2:latest',
        messages=[
            {
                'role': 'system',
                'content': "You are an LLM that determines which SQL table to use based on the user's question. The user will ask a question about either a grocery store or a movie database, and you will determine which table to use and return the name of the table. Answer with only 1 word, either 'Store' or 'Movies'. If the question is not about either of these topics, respond with 'No valid table found.'. DO NOT RESPOND WITH ANYTHING ELSE, ONLY THE TABLE NAME, OR 'No valid table found.' IF THE QUESTION IS NOT ABOUT EITHER TOPIC.",
            },
            {
                'role': 'user',
                'content': user_prompt
            },
        ],
    )
    
    table_name = determined_prompt['message']['content'].strip()
    if table_name not in sql_prompts:
        return jsonify({"response": "No valid table found."})
    system_prompt = sql_prompts.get(table_name, "")
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

    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS store (
    #         product TEXT,
    #         orders INTEGER,
    #         stock INTEGER
    #     );
    # """)

    # # Clear the store table before inserting new data
    # cur.execute("DELETE FROM store;")

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
    return jsonify({"response": response['message']['content']})

@app.route('/pdf/process', methods=['POST'])
def process_pdf_contents():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No selected files"}), 400

    all_char_chunks = []
    for file in files:
        filename = file.filename
        with pdfplumber.open(file) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
        def chunk_text_by_chars(text, chunk_size=500):
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-100)]
        for p in range(len(pages)):
            if not pages[p]:
                continue
            for i, chunk in enumerate(chunk_text_by_chars(pages[p])):
                # pdfplumber does not provide .metadata directly on the file object.
                # Instead, use pdfplumber's pdf.metadata attribute.
                all_char_chunks.append({
                    "text": chunk,
                    "page": p + 1,
                    "chunk_index": i,
                    "source": filename,
                    "doc_title": pdf.metadata.get('Title', "") if pdf.metadata else "N/A",
                    "author": pdf.metadata.get('Author', "") if pdf.metadata else "N/A",
                    "subject": pdf.metadata.get('Subject', "") if pdf.metadata else "N/A",
                })

    print(f"Total chunks created: {len(all_char_chunks)}")
    sentences = [c["text"] for c in all_char_chunks]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sentences)
    print("Embeddings Successfully generated using sentence transformer model.")

    # Delete table items
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS items;")
        conn.commit()
    print("Dropped existing items table.")

    # Use the global conn and register_vector
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                embedding VECTOR(384),
                content TEXT,
                page INTEGER,
                source TEXT,
                chunk_index INTEGER,
                doc_title TEXT,
                author TEXT,
                subject TEXT
            );
        """)
        conn.commit()

    # Optionally clear the table, or comment out to append
    with conn.cursor() as cur:
        cur.execute("DELETE FROM items;")
        conn.commit()

    with conn.cursor() as cur:
        for embedding, content, page, chunk_index, source, doc_title, author, subject in zip(
            embeddings, [c["text"] for c in all_char_chunks],
            [c["page"] for c in all_char_chunks],
            [c["chunk_index"] for c in all_char_chunks],
            [c["source"] for c in all_char_chunks],
            [c["doc_title"] for c in all_char_chunks],
            [c["author"] for c in all_char_chunks],
            [c["subject"] for c in all_char_chunks]
        ):
            cur.execute(
                "INSERT INTO items (embedding, content, page, chunk_index, source, doc_title, author, subject) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                (embedding, content, page, chunk_index, source, doc_title, author, subject)
            )
        conn.commit()
    print("Data inserted successfully.")
    return jsonify({"message": "PDFs processed and data inserted successfully."})

@app.route('/pdf/context', methods=['POST'])
def get_pdf_context():
    query = request.json.get('query', '')
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query])[0]
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute("SELECT id, content, embedding, page, chunk_index, doc_title, author, subject FROM items;")
        rows = cur.fetchall()
        print("Number of items in the database:", len(rows))
        similarities = []
        for row in rows:
            item_id, content, embedding, page, chunk_index, doc_title, author, subject = row
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((item_id, content, similarity, page, chunk_index, doc_title, author, subject))
        similarities.sort(key=lambda x: x[2], reverse=True)
        print("Similar found")
        return jsonify({"response": f"Most similar chunk: [Context from file: {similarities[0][1]}, Page number in PDF: {similarities[0][3]}, Chunk index: {similarities[0][4]}, Document Title: {similarities[0][5]}, Author: {similarities[0][6]}, Subject: {similarities[0][7]}], 2nd most similar chunk: [Context from file: {similarities[1][1]}, Page number in PDF: {similarities[1][3]}, Chunk index: {similarities[1][4]}, Document Title: {similarities[1][5]}, Author: {similarities[1][6]}, Subject: {similarities[1][7]}]"})
def chunk_text_by_chars(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-100)]

def scrape_webpage(url):
    print(f"Scraping webpage: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text()

    print(f"Extracted content length: {len(content)} characters")

    processed_chunks = []
    chunks = chunk_text_by_chars(content)
    for i, chunk in enumerate(chunks):
        processed_chunks.append({
            "text": chunk,
            "source": url,
            "chunk_index": i
        })

    embeddings = model.encode([c["text"] for c in processed_chunks])

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS webscraped (
                id SERIAL PRIMARY KEY,
                embedding VECTOR(384),
                content TEXT,
                source TEXT,
                chunk_index INTEGER
            );
        """)
        conn.commit()   
    
    # Delete existing data in the webscraped table
    with conn.cursor() as cur:
        cur.execute("DELETE FROM webscraped;")
        conn.commit()
    print("Deleted existing data in webscraped table.")

    with conn.cursor() as cur:
        for embedding, content, source, chunk_index in zip(embeddings, [p["text"] for p in processed_chunks],
                                                            [p["source"] for p in processed_chunks],
                                                            [p["chunk_index"] for p in processed_chunks]):
            cur.execute(
                "INSERT INTO webscraped (embedding, content, source, chunk_index) VALUES (%s, %s, %s, %s);",
                (embedding, content, source, chunk_index)
            )
        conn.commit()
    print("Data inserted successfully.")
    return embeddings.tolist()  # Return embeddings as a list for JSON serialization

# Example Webpages:
# https://realpython.com/beautiful-soup-web-scraper-python/ (Web Scraper)
# https://ftb.fandom.com/wiki/Latex (Latex MMC Resource)
@app.route('/webpage/process', methods=['POST'])
def process_webpage_contents():
    if 'url' not in request.json:
        return jsonify({"error": "No URL provided"}), 400
    url = request.json['url']
    embeddings = scrape_webpage(url)
    return embeddings

@app.route('/webpage/context', methods=['POST'])
def get_webpage_context():
    query = request.json.get('query', '')
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query])[0]
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute("SELECT id, content, embedding, source, chunk_index FROM webscraped;")
        rows = cur.fetchall()
        print("Number of items in the database:", len(rows))
        similarities = []
        for row in rows:
            item_id, content, embedding, source, chunk_index = row
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((item_id, content, similarity, source, chunk_index))
        similarities.sort(key=lambda x: x[2], reverse=True)
        print("Similar found")
        return jsonify({"response": f"Most similar chunk: [Context from file: {similarities[0][1]}, Webpage Link: {similarities[0][3]}, Chunk index: {similarities[0][4]}], 2nd most similar chunk: [Context from file: {similarities[1][1]}, Webpage Link: {similarities[1][3]}, Chunk index: {similarities[1][4]}]"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
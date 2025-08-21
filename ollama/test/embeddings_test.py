from sentence_transformers import SentenceTransformer
import pandas as pd
import psycopg2
from pgvector.psycopg2 import register_vector
import pdfplumber
import os

content = ""
with pdfplumber.open("ollama/test/daryl_resume.pdf") as pdf:
    first_page = pdf.pages[0]
    content = first_page.extract_text()
    # print(content)

# Character Chunking
char_chunks = []

def chunk_text_by_chars(text, chunk_size=500):
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size-100)]

# Add Metadata to each chunk
for i, chunk in enumerate(chunk_text_by_chars(content)):
    char_chunks.append({
        "text": chunk,
        "page": 1,  # since you used first_page
        "chunk_index": i,
        "source": "daryl_resume.pdf"
    })

sentences = [c["text"] for c in char_chunks]

conn = psycopg2.connect(dbname="mydb", user="darylho", password=os.getenv("DATABASE_PASSWORD"),)
register_vector(conn)

print("Connected to PostgreSQL database.")


model = SentenceTransformer("all-MiniLM-L6-v2")

# sentences = [
#     "I am taking Artificial Intelligence at Santa Clara University.",
#     "I am taking Computer Vision at Santa Clara University.",
#     "I am taking Machine Learning at Santa Clara University.",
#     "I like swimming in my free time.",
#     "Hiking in my free time is fun.",
#     "Puzzle games are hard.",
#     "I like to play chess.",
#     "I am a software engineer.",
# ]

embeddings = model.encode(sentences)
embeddings_df = pd.DataFrame(embeddings)

# embeddings = embeddings.tolist()  # Convert to list for insertion into PostgreSQL
# print(embeddings)

print("Embeddings Successfully generated.")

# Clear the items table before inserting new data
cur = conn.cursor()
cur.execute("DELETE FROM items;")
conn.commit()

with conn.cursor() as cur:
    for embedding, sentences, page, chunk_index, source in zip(embeddings, sentences, [c["page"] for c in char_chunks],
                                                            [c["chunk_index"] for c in char_chunks],
                                                            [c["source"] for c in char_chunks]):
        cur.execute(
            "INSERT INTO items (embedding, content, page, chunk_index, source) VALUES (%s, %s, %s, %s, %s);",
            (embedding, content, page, chunk_index, source)  # Ensure these variables are defined
        )
    conn.commit()

print("Data inserted successfully.")

with conn.cursor() as cur:
    cur.execute("SELECT id, embedding FROM items LIMIT 5;")
    rows = cur.fetchall()
    for row in rows:
        print(row[2])

print("Data retrieved successfully.")
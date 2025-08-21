import ollama
from sentence_transformers import SentenceTransformer
import pandas as pd
import psycopg2
from pgvector.psycopg2 import register_vector
import pdfplumber
from sklearn.metrics.pairwise import cosine_similarity

content = ""
pages = []
with pdfplumber.open("ollama/test/photon_offer_letter.pdf") as pdf:
    pages = [page.extract_text() for page in pdf.pages]

print(f"Total pages extracted: {len(pages)}")
# Character Chunking
char_chunks = []
def chunk_text_by_chars(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-100)]

# Add Metadata to each chunk
for p in range(len(pages)):
    print(f"Processing page {p + 1} of {len(pages)}")
    for i, chunk in enumerate(chunk_text_by_chars(pages[p])):
        char_chunks.append({
            "text": chunk,
            "page": p + 1,
            "chunk_index": i,
            "source": "daryl_resume.pdf"
        })
print(f"Total chunks created: {len(char_chunks)}")
sentences = [c["text"] for c in char_chunks]

register_vector(conn)
print("Connected to PostgreSQL database.")

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

# Embeddings using Sentence Transformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(sentences)
# embeddings_df = pd.DataFrame(embeddings)
print("Embeddings Successfully generated using sentence transformer model.")

# # Embeddings using Ollama Embedding Model
# embeddings = [ollama.embeddings(model='nomic-embed-text', prompt=s).get('embedding', 'No embedding found') for s in sentences]
# print("Embeddings Successfully generated using ollama embedding model.")

# Clear the items table before inserting new data
cur = conn.cursor()
cur.execute("DELETE FROM items;")
conn.commit()

with conn.cursor() as cur:
    for embedding, content, page, chunk_index, source in zip(embeddings, sentences, [c["page"] for c in char_chunks],
                                                            [c["chunk_index"] for c in char_chunks],
                                                            [c["source"] for c in char_chunks]):
        cur.execute(
            "INSERT INTO items (embedding, content, page, chunk_index, source) VALUES (%s, %s, %s, %s, %s);",
            (embedding, content, page, chunk_index, source)
        )
    conn.commit()
print("Data inserted successfully.")

query = input("Enter a query to search for similar items: ")
query_embedding = model.encode([query])[0]
# query_embedding = ollama.embeddings(model='nomic-embed-text', prompt=query).get('embedding', 'No embedding found')

with conn.cursor() as cur:
    cur.execute("SELECT id, content, embedding FROM items;")
    rows = cur.fetchall()
    print("Number of items in the database:", len(rows))
    similarities = []
    for row in rows:
        item_id, content, embedding = row
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        similarities.append((item_id, content, similarity))
    similarities.sort(key=lambda x: x[2], reverse=True)

    # Current Test Code
    print("Top 5 similar items:")
    for item in similarities[:5]:
        print(f"ID: {item[0]}, Content: {item[1]}..., Similarity: {item[2]:.4f}")
        print("-" * 50)
        print("-" * 50)
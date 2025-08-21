import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector

# visited = set()
all_chunks = []

model = SentenceTransformer("all-MiniLM-L6-v2")

register_vector(conn)
print("Connected to PostgreSQL database.")

def chunk_text_by_chars(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-100)]

def scrape_webpage(url):
    # if depth > 2 or url in visited:
    #     return
    # visited.add(url)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text()

    process_web_content(content, url)
    # for link in soup.find_all('a', href=True):
    #     if link['href'].startswith(domain):
    #         scrape_webpage(link['href'], depth + 1)
    return

def process_web_content(content, url):
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

    with conn.cursor() as cur:
        for embedding, content, source, chunk_index in zip(embeddings, [p["text"] for p in processed_chunks],
                                                            [p["source"] for p in processed_chunks],
                                                            [p["chunk_index"] for p in processed_chunks]):
            cur.execute(
                "INSERT INTO items (embedding, content, source, chunk_index) VALUES (%s, %s, %s, %s);",
                (embedding, content, source, chunk_index)
            )
        conn.commit()
    print("Data inserted successfully.")
    all_chunks.extend(processed_chunks)
    return

scrape_webpage("https://shminer.miraheze.org/wiki/Construct")
print(f"Total chunks processed: {len(all_chunks)}")
print(all_chunks[:5])  # Print first 5 chunks for verification
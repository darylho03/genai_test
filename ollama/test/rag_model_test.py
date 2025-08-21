import ollama

import psycopg2
from pgvector.psycopg2 import register_vector
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import time
import sys
import logging
from pythonjsonlogger import jsonlogger
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg2.connect(
    dbname="mydb",
    user="darylho",
    password=os.getenv("DATABASE_PASSWORD"),
    host="localhost",
    port=5432
    
)
register_vector(conn)
print("Connected to PostgreSQL database.")

logger = logging.getLogger(__name__)
def initialize_logging():
    """Initialize logging configuration."""
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)

    fileHandler = logging.FileHandler("app.log")

    format_output = jsonlogger.JsonFormatter('%(levelname)s : %(name)s : %(message)s : %(asctime)s')

    stdout_handler.setFormatter(format_output)

    fileHandler.setFormatter(format_output)

    logger.addHandler(stdout_handler)
    logger.addHandler(fileHandler)
initialize_logging()

def pdf_embeddings(file, progress_callback=None):
    content = ""
    pages = []
    with pdfplumber.open(file) as pdf:
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
                "source": "photon_offer_letter.pdf"
            })
        if progress_callback:
            progress_callback((p + 1) / len(pages))
    print(f"Total chunks created: {len(char_chunks)}")
    sentences = [c["text"] for c in char_chunks]

    # Embeddings using Sentence Transformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sentences)
    print("Embeddings Successfully generated using sentence transformer model.")

    # Create items table if it doesn't exist
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                embedding VECTOR(384),
                content TEXT,
                page INTEGER,
                chunk_index INTEGER,
                source TEXT
            );
        """)
        conn.commit()   
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
    return embeddings

def get_pdf_context(query):
    query_embedding = model.encode([query])[0]
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute("SELECT id, content, embedding, page, chunk_index FROM items;")
        rows = cur.fetchall()
        print("Number of items in the database:", len(rows))
        similarities = []
        for row in rows:
            item_id, content, embedding, page, chunk_index = row
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((item_id, content, similarity, page, chunk_index))
        similarities.sort(key=lambda x: x[2], reverse=True)
        print("Similar found")
        return (f"Context from file: {similarities[0][1]}, Page number in PDF: {similarities[0][3]}, Chunk index: {similarities[0][4]}")

def change_starter_message():
    st.session_state.messages = [{"role": "assistant", "content": "PDF Context Assistant"}]

add_selectbox = st.sidebar.selectbox(
    'Select a Chatbot Character',
    ('PDF Context Assistant'),
    key="character",
    on_change=change_starter_message,
)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "PDF Context Assistant"}]

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    file_id = uploaded_file.name
    if st.session_state.get("last_uploaded_file") != file_id:
        progress_bar = st.progress(0, text="Processing PDF...")
        def update_progress(progress):
            progress_bar.progress(progress, text=f"Processing PDF... {int(progress*100)}%")
        embeddings = pdf_embeddings(uploaded_file, progress_callback=update_progress)
        progress_bar.empty()  # Remove the progress bar when done
        st.session_state["pdf_processed"] = True
        st.session_state["embeddings"] = embeddings
        st.session_state["last_uploaded_file"] = file_id
else:
    st.warning("Please upload a PDF file to proceed.")

for message in st.session_state.messages:
    avatar = None
    if message["role"] == "assistant":
        avatar = "🤖"
    # Change this avatar later to a more appropriate one
    elif message["role"] == "user":
        avatar = "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = ""
        try:
          context = get_pdf_context(prompt)
          assistant_response = ollama.chat(
              model='llama3.2:latest',
              messages=[
                  {
                      'role': 'system',
                      'content': "You are a PDF Context Assistant. You will answer questions with added context provided from a PDF document. The context is: " + context
                  },
                  {
                      'role': 'user',
                      'content': prompt
                  },
              ],
          )
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            st.error("An error occurred while generating the response. Please try again later.")
            assistant_response = "An error occurred while generating the response. Please try again later."

        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response['message']['content'].split():
            full_response += chunk + " "
            time.sleep(0.1)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    message = {
        "role": "assistant",
        "content": full_response,
        "avatar": "🤖"
    }
    st.session_state.messages.append(message)
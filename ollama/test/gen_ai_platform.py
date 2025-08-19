import streamlit as st
import time
# import sys
# import logging
# from pythonjsonlogger import jsonlogger
import requests


# logger = logging.getLogger(__name__)
# def initialize_logging():
#     """Initialize logging configuration."""
#     logger.setLevel(logging.INFO)

#     stdout_handler = logging.StreamHandler(stream=sys.stdout)

#     fileHandler = logging.FileHandler("app.log")

#     format_output = jsonlogger.JsonFormatter('%(levelname)s : %(name)s : %(message)s : %(asctime)s')

#     stdout_handler.setFormatter(format_output)

#     fileHandler.setFormatter(format_output)

#     logger.addHandler(stdout_handler)
#     logger.addHandler(fileHandler)
# initialize_logging()

starter_messages = {
    'Icely Puzzles': "Chess Battle Advanced",
    'Balatro University': "I'm only here for the muhnee",
    'NairoMK': "Don't talk to me drone, YA LOST",
    'Custom': "You can enter a custom system prompt.",
    'PDF Context Assistant': "I give you context from PDF documents to answer your questions.",
    'SQL Query Assistant': "I give information based on a custom Shop SQL database and Movie SQL database.",
    'Web Scraper': "I give information off of a website link."
}

def change_starter_message():
    selected = st.session_state["character"]
    st.session_state.messages = [{"role": "assistant", "content": starter_messages[selected]}]

add_selectbox = st.sidebar.selectbox(
    'Select a Chatbot Character',
    ('Icely Puzzles', 'Balatro University', 'NairoMK', 'Custom', 'PDF Context Assistant', 'SQL Query Assistant', 'Web Scraper'),
    key="character",
    on_change=change_starter_message,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": starter_messages[add_selectbox]}]

# Render any additional UI elements based on the selected chatbot character
match add_selectbox:
    case 'Custom':
        custom_prompt = st.text_area("Enter a custom system prompt:", value="", height=200)
    case 'Web Scraper':
        webpage = st.text_area("Enter a valid website link:", value="", height=100)
    case 'PDF Context Assistant':
        uploaded_files = st.file_uploader("Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            file_ids = [f.name for f in uploaded_files]
            if st.session_state.get("last_uploaded_files") != file_ids:
                progress_bar = st.progress(0, text="Processing PDFs...")
                def update_progress(progress):
                    progress_bar.progress(progress, text=f"Processing PDFs... {int(progress*100)}%")
                print(f"Processing files: {file_ids}")
                # Prepare files for requests.post
                files = [('files', (f.name, f, 'application/pdf')) for f in uploaded_files]
                embeddings = requests.post("http://localhost:5050/pdf/process", files=files)
                progress_bar.empty()  # Remove the progress bar when done
                st.session_state["pdf_processed"] = True
                st.session_state["embeddings"] = embeddings
                st.session_state["last_uploaded_files"] = file_ids
            else:
                st.warning("Please upload PDF files to proceed.")
    case '_':
        # Do nothing for other characters
        pass

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
        is_error = False
        full_response = ""
        assistant_response = ""
        try:
          match add_selectbox:
            case 'PDF Context Assistant':
                if not st.session_state.get("pdf_processed", False):
                    st.error("Please upload a PDF file to proceed.")
                    is_error = True
                else:
                    context = requests.post("http://localhost:5050/pdf/context", json={'query': prompt}).json()
                    print(context)
                    assistant_response = requests.post("http://localhost:5050/chatbot/custom", json={'user_prompt': prompt, 'system_prompt': f'You are a PDF Context Assistant. You will answer questions with added context provided from a PDF document. The context is: {context}'})
            case 'SQL Query Assistant':
                  assistant_response = requests.post("http://localhost:5050/sql", json={'prompt': prompt})
            case 'Custom':
                if not prompt:
                    st.error("Please enter a custom system prompt.")
                    is_error = True
                else:
                    assistant_response = requests.post("http://localhost:5050/chatbot/custom", json={'user_prompt': prompt, 'system_prompt': custom_prompt})
            case 'Web Scraper':
                embeddings = requests.post("http://localhost:5050/webpage/process", json={'url': webpage})
                context = requests.post("http://localhost:5050/webpage/context", json={'query': prompt}).json()
                assistant_response = requests.post("http://localhost:5050/chatbot/custom", json={'user_prompt': prompt, 'system_prompt': f'You are a Web Scraping Context Assistant. You will answer questions with added context provided from information scraped from a website. The context is: {context}'})
            case _:
                print("Using character:", add_selectbox)
                assistant_response = requests.post(f"http://localhost:5050/chatbot/{add_selectbox}", json={'prompt': prompt})
        except Exception as e:
            # logger.error(f"Error during chat: {e}")
            st.error("An error occurred while generating the response. Please try again later.")
            assistant_response = "An error occurred while generating the response. Please try again later."
            is_error = True
        if not is_error:
            if assistant_response.status_code == 200:
                try:
                    response_json = assistant_response.json()
                    print(response_json)
                    for chunk in response_json['response'].split():
                        full_response += chunk + " "
                        time.sleep(0.1)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    # logger.error(f"Error decoding JSON: {e}")
                    st.error("The server did not return valid JSON.")
                    is_error = True
            else:
                st.error(f"API error: {assistant_response.status_code}\n{assistant_response.text}")
                is_error = True

    message = {
        "role": "assistant",
        "content": full_response,
        "avatar": "🤖"
    }
    st.session_state.messages.append(message)
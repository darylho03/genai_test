import streamlit as st
import pandas as pd
import time
import ollama
import sys
import logging
from pythonjsonlogger import jsonlogger

starter_message = {
    'Icely Puzzles': "Chess Battle Advanced",
    'Balatro University': "I'm only here for the muhnee",
    'NairoMK': "Don't talk to me drone.",
    'Custom': "You can customize the prompt above."
}
avatars = {
    'Icely Puzzles': "https://yt3.googleusercontent.com/vkFxjsCdOhP3u4KSmRFhCUWwvGIuCaFCbFrNQfJ1OTF1WE72Jl7TFId-ayvvScfAsO73E-5TsQ=s160-c-k-c0x00ffffff-no-rj",
    'Balatro University': "https://yt3.googleusercontent.com/8oXxQ1ncoByQpa6PDk2reaw8j0kD4P0ecFlqtvIY9Eld25dIS3sMW2Z6Sv5upitTRMPPd8yO=s160-c-k-c0x00ffffff-no-rj",
    'NairoMK': "https://yt3.googleusercontent.com/ytc/AIdro_lP7PSQVrngo9DMKv8_vtDgI80ckakDJ3LxDYBKWWA3c0M=s160-c-k-c0x00ffffff-no-rj"
}

models = {
    1: 'llama3.2:latest',
    2: 'deepseek-r1:1.5b',
    3: 'gemma3:1b',
    4: 'qwen3:1.7b',
}
system_prompts = {
    'Icely Puzzles': 'You are a puzzle game content creator named IcelyPuzzles. You create content showcasing or playthroughs of popular or niche puzzle games. You also have an obsession with Chess Evolved Online, an online chess variant with custom pieces. You also have an inside joke on your channel called "Chess Battle Advaced", a game based on Chess Evolved Online also with custom pieces, but is mainly a meme to you because of its ridiculous title screen music. No matter what, you must reference Chess Battle Advanced or CBA (the abbreviation) at least once in every response. If it is ever relevant in responses, your favorite puzzle games are "Baba is You", "Lingo", and "Patrick\'s Parabox". You also don\'t typically create a narrative in your commentary and stray closer to the technical side of the game, such as game design decisions, strategies, tactics, and mechanics. For example, when you cover a game you\'re playing for the first time, you immediately point out any bugs or odd game design decisions you see and joke about them (usually just saying Chess Battle Advanced in the presence of one of them). You also have a very dry sense of humor, and you often make sarcastic comments about the games you play. You are also very critical of games that you find to be poorly designed or unbalanced, and you are not afraid to express your opinions on them. You also highly praise good puzzle design, as a puzzle game enthusiast and former puzzle game playtester, you have a keen eye for what makes a good puzzle game. You also have a very analytical mind, and you often break down games into their individual components to analyze them. You also have a very strong sense of aesthetics, and you often comment on the visual design of the games you play. The following is an example of an intro to a video you would make of a niche puzzle game that just released called "Threadbound": "Welcome to a game called Threadbound, which is a puzzle platformer all about writing your own laws of physics, and from what I heard from Steam reviews, this is incredible. There is around 2-3 hours of gameplay in this demo, starts kinda slow but oh my god. Its so polished and good already. Like I don\'t normally say "must play" but that is a good... really fitting label for this game. Let\'s get into the gameplay now. Also this is not sponsored."',
    'Balatro University': 'You are a Balatro content creator named Balatro University. You mainly create content on Balatro, a roguelike deckbuilding game where you play poker hands to reach higher and higher scores. You are one of the best, if not the best, Balatro player in the world, and you are known for your high scores and your ability to play the game at a high level. Your content is also very informative and you explain every play you make in great detail, explaining why you make every play and why you don\'t make some others. Your analytical and strategic mind comes from your background with having a PhD in Mathematics and being a former math professor. Your main words/phrases that are iconic to your YouTube channel and Twitch livestream are "muhnee", used to replace the word "money" at times when your current emphasis in Balatro is building economy, "go next", used when you exit the shop in Balatro.',
    'NairoMK': 'You are a content creator named NairoMK, or Nairo for short, but mainly referred to as NairoMK. You mainly create content on Super Smash Bros. Ultimate and Mario Kart, but rarely play variety. You are a very competitive player, but also a very good player, and a former professional player in Super Smash Bros. Ultimate at tournaments, but due to unfortunate circumstanses you will never bring up ever, you now only create content for it online. Your main personality is sarcastically cocky/arrogant and will often trashtalk your opponents or members of chat in a humorous manner. Your main common words/phrases that are iconic to your YouTube channel and YouTube livestream are "YOU KNOW THE VIBES!", used as an intro for videos or when destroying opponents in smash, "KICKED IN YO CHEST!", used when your character in smash uses a move that kicks an opponent, "YA LOST!", used when you believe you or someone you are watching is about to destroy an opponent, "Your gem is crushed/eviscerated", used when you ban a user in chat or used when blocking a user on smash ultimate, typically for lagging, "MID!", when particular characters appear on screen or are mentioned, those characters being Sephiroth, Cloud, and Palutena (your main at past tournaments). You also have a tendency of bringing up Sephiroth in the most seemingly random points in your videos, due to your disappointment in how weak the character is in smash, often bringing him up to compare him to other characters in the game, such as "Sephiroth would have died from that" or "Another character better than Sephiroth", often reffering to him as "MID". When responding to prompts, be sure to FULLY CAPITALIZE some words, such as "YOU KNOW THE VIBES!" or "KICKED IN YO CHEST!" to simulate that you are yelling them and emphasizing them. For example, here is what an intro to a video you would make of a Super Smash Bros. Ultimate tournament reaction video would look like: "YOUTUBE! YOU KNOW THE VIBES! Today we are going to be reacting to Kagaribi 13, the largest Smash Ultimate tournament in HISTORY, hosted in Japan! Today, we will be watching pools, hopefully seeing some of our predictions some true, and hopefully seeing AMERICA pull through. That means YOU "LIGHT", if I see you lose to Miya\'s game & watch when I literally TRAINED you last week, your gem is eviscerated. But anyway, let\'s start watching some matches."',
}

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


def change_starter_message():
    st.session_state.messages = [{"role": "assistant", "content": starter_message[st.session_state.character]}]

add_selectbox = st.sidebar.selectbox(
    'Select a Chatbot Character',
    ('Icely Puzzles', 'Balatro University', 'NairoMK', 'Custom'),
    key="character",
    on_change=change_starter_message,
)

if add_selectbox == 'Custom':
    system_prompts[st.session_state.character] = st.text_area("Enter a custom system prompt:", value="", height=200)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": starter_message[st.session_state.character]}]


for message in st.session_state.messages:
    avatar = None
    if message["role"] == "assistant":
        avatar = avatars[st.session_state.character] if st.session_state.character in avatars else "🤖"
    # Change this avatar later to a more appropriate one
    elif message["role"] == "user":
        avatar = "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=avatars[st.session_state.character] if st.session_state.character in avatars else "🤖"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = ""
        try:
          assistant_response = ollama.chat(
              model='llama3.2:latest',
              messages=[
                  {
                      'role': 'system',
                      'content': system_prompts[add_selectbox]
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
        "avatar": avatars[st.session_state.character] if st.session_state.character in avatars else "🤖"
    }
    st.session_state.messages.append(message)
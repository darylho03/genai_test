import ollama
import sys
import logging
from pythonjsonlogger import jsonlogger

models = {
    1: 'llama3.2:latest',
    2: 'deepseek-r1:1.5b',
    3: 'gemma3:1b',
    4: 'qwen3:1.7b',
}
system_prompts = {
    'Icely Puzzles': 'You are a puzzle game content creator named IcelyPuzzles. You create content showcasing or playthroughs of popular or niche puzzle games. You also have an obsession with Chess Evolved Online, an online chess variant with custom pieces. You also have an inside joke on your channel called "Chess Battle Advaced", a game based on Chess Evolved Online also with custom pieces, but is mainly a meme to you because of its ridiculous title screen music. No matter what, you must reference Chess Battle Advanced or CBA (the abbreviation) at least once in every response. If it is ever relevant in responses, your favorite puzzle games are "Baba is You", "Lingo", and "Patrick\'s Parabox". You also don\'t typically create a narrative in your commentary and stray closer to the technical side of the game, such as game design decisions, strategies, tactics, and mechanics. For example, when you cover a game you\'re playing for the first time, you immediately point out any bugs or odd game design decisions you see and joke about them (usually just saying Chess Battle Advanced in the presence of one of them). You also have a very dry sense of humor, and you often make sarcastic comments about the games you play. You are also very critical of games that you find to be poorly designed or unbalanced, and you are not afraid to express your opinions on them. You also highly praise good puzzle design, as a puzzle game enthusiast and former puzzle game playtester, you have a keen eye for what makes a good puzzle game. You also have a very analytical mind, and you often break down games into their individual components to analyze them. You also have a very strong sense of aesthetics, and you often comment on the visual design of the games you play. The following is an example of an intro to a video you would make of a niche puzzle game that just released called "Threadbound": "Welcome to a game called Threadbound, which is a puzzle platformer all about writing your own laws of physics, and from what I heard from Steam reviews, this is incredible. There is around 2-3 hours of gameplay in this demo, starts kinda slow but oh my god. Its so polished and good already. Like I don\'t normally say "must play" but that is a good... really fitting label for this game. Let\'s get into the gameplay now. Also this is not sponsored."',
    'Balatro University': '',
    'NairoMK': 'You are a content creator named NairoMK, or Nairo for short, but mainly referred to as NairoMK. You mainly create content on Super Smash Bros. Ultimate and Mario Kart, but rarely play variety. You are a very competitive player, but also a very good player, and a former professional player in Super Smash Bros. Ultimate at tournaments, but due to unfortunate circumstanses you will never bring up ever, you now only create content for it online. Your main personality is sarcastically cocky/arrogant and will often trashtalk your opponents or members of chat in a humorous manner. Your main common words/phrases that are iconic to your channel and livestream are "YOU KNOW THE VIBES!", used as an intro for videos or when destroying opponents in smash, "KICKED IN YO CHEST!", used when your character in smash uses a move that kicks an opponent, "YA LOST!", used when you believe you or someone you are watching is about to destroy an opponent, "Your gem is crushed/eviscerated", used when you ban a user in chat or used when blocking a user on smash ultimate, typically for lagging, "MID!", when particular characters appear on screen or are mentioned, those characters being Sephiroth, Cloud, and Palutena (your main at past tournaments). You also have a tendency of bringing up Sephiroth in the most seemingly random points in your videos, due to your disappointment in how weak the character is in smash, often bringing him up to compare him to other characters in the game, such as "Sephiroth would have died from that" or "Another character better than Sephiroth", often reffering to him as "MID". When responding to prompts, be sure to FULLY CAPITALIZE some words, such as "YOU KNOW THE VIBES!" or "KICKED IN YO CHEST!" to simulate that you are yelling them and emphasizing them. For example, here is what an intro to a video you would make of a Super Smash Bros. Ultimate tournament reaction video would look like: "YOUTUBE! YOU KNOW THE VIBES! Today we are going to be reacting to Kagaribi 13, the largest Smash Ultimate tournament in HISTORY, hosted in Japan! Today, we will be watching pools, hopefully seeing some of our predictions some true, and hopefully seeing AMERICA pull through. That means YOU "LIGHT", if I see you lose to Miya\'s game & watch when I literally TRAINED you last week, your gem is eviscerated. But anyway, let\'s start watching some matches."',
}
message_history = []

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

def chat_main():
    choice = int(input("Choose an option:\n1. Chat with Bots\n2. View Chat History\n3. Quit\nEnter the number of your choice: "))
    if choice == 1:
        chat_with_bots()
    elif choice == 2:
        view_chat_history()
    elif choice == 3:
        print("Exiting the chat application.")
        sys.exit(0)

def chat_with_bots():
    initialize_logging()
    while True:
        model_choice = int(input("Choose a model:\n1. Llama 3.2\n2. DeepSeek R1\n3. Gemma 3\n4. Qwen 3\nEnter the number of your choice: "))
        if model_choice not in models:
            if model_choice == 0:
                break
            print("Invalid choice. Please try again.")
            continue
        chatbot = (input("Choose a chatbot personality:\n1. Icely Puzzles\n2. Balatro University\n3. NairoMK\nEnter the NAME of your choice: "))
        if chatbot not in system_prompts:
            print("Invalid choice. Please try again.")
            continue
        user_prompt = input("Please enter your question: ")
        logger.info(f"User prompt: {user_prompt}")
        response = ollama.chat(
            model=models[model_choice],
            messages=[
                {
                    'role': 'system',
                    'content': system_prompts[chatbot]
                },
                {
                    'role': 'user',
                    'content': user_prompt,
                },
            ],
        )
        interaction = {
            'model': models[model_choice],
            'chatbot': chatbot,
            'prompt': user_prompt,
            'response': response['message']['content'],
        }
        message_history.append(interaction)
        logger.info("Interaction logged.")
        logger.info(f"Model: {models[model_choice]}, Chatbot: {chatbot}, Prompt: {user_prompt}, Response: {response['message']['content']}")
        print(response['message']['content'])

def view_chat_history():
    if not message_history:
        print("No chat history available.")
        return
    print("Chat History:")
    for i, interaction in enumerate(message_history, start=1):
        print(f"{i}. Model: {interaction['model']}, Chatbot: {interaction['chatbot']}, Prompt: {interaction['prompt']}, Response: {interaction['response']}")



if __name__ == "__main__":
    while True:
        chat_main()
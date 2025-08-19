import ollama
import sys
import logging
from pythonjsonlogger import jsonlogger

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

def main():
    initialize_logging()

    # Prompt the user for input
    user_prompt = input("Please enter your question: ")
    logger.info(f"User prompt: {user_prompt}")
    try:
        response = ollama.chat(
            model='llama3.2:latest',
            messages=[
                {
                    'role': 'user',
                    'content': user_prompt,
                },
            ],
        )
        logger.info("Model response received.")
        print(response['message']['content'])
        logger.info(f"Response content: {response['message']['content']}")
    except Exception as e:
        logger.error(f"Error during chat: {e}")

if __name__ == "__main__":
    main()
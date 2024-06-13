# Main entry point for the chatbot

# main.py
import os

import chatbot
import database
from gpt_manager import GPTManager

def main():

    db_manager = database.DatabaseManager()
    lm_manager = GPTManager(os.getenv("OPENAI_API_KEY"))  # This can be replaced with any other LM implementation
    bot = chatbot.Chatbot(db_manager, lm_manager)

    bot.start_conversation()

if __name__ == "__main__":
    main()

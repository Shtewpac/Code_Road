# Chatbot logic goes here

# chatbot.py
import json
from language_model import LanguageModel

class Chatbot:
    def __init__(self, db_manager, language_model: LanguageModel):
        self.db_manager = db_manager
        self.language_model = language_model
        print("Chatbot initialized.")

    def start_conversation(self):
        print("Starting conversation... Type 'quit' to exit.")

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                break

            lm_response = self.language_model.get_response(user_input)
            self.respond(lm_response)

    def respond(self, message):
        try:
            json_response = json.loads(message)
            # print(f"JSON response: {json_response}")

            # Check for 'response', 'error', and 'result' keys
            response_message = json_response.get("response") or json_response.get("error") or json_response.get("result") or json_response.get("message")
            if response_message is not None:
                print(f"Chatbot: {response_message}")
            else:
                print("Chatbot: Sorry, I didn't understand that.")
        except json.JSONDecodeError:
            print(f"Received non-JSON response: {message}")

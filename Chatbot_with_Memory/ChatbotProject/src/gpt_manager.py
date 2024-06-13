# gpt3_manager.py

import openai
from language_model import LanguageModel

class GPTManager(LanguageModel):
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in getting response from openai: {e}")
            return None

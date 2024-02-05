"""
Author: Hang Yan
Date created: 2023/8/9
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

import os
import sys
import json
import openai


from .redis_conn import insert_system_prompt_if_not_exists, save_message, get_conversation_history

parent_dir = os.path.dirname(os.path.abspath("."))
sys.path.append(parent_dir)

from config import HISTORY_SIZE, OPENAI_API_KEY, prompt_settings, PromptEnum


openai.api_key = OPENAI_API_KEY
user_identifier = "Interviewer3"
conversation_key = f"conversation:{user_identifier}"


class GptHandler:
    def __init__(self):
        self.key = None
        self.sentence = ""

    def init_prompt(self, prompt_type, version=None):
        system_prompt = "You are a helpful assistant."
        insert_system_prompt_if_not_exists(self.key, system_prompt)

    def generate_key_name(self, user, prompt_type):
        self.key = f"{user}"

    def send_openai_request(self, messages):
        stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            temperature=0.4,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=messages,
            stream=True,
        )
        return stream

    def remove_duplicate_messages(self, conversation_history_list):
        unique_history = []
        for conversation_history in conversation_history_list:
            if conversation_history not in unique_history:
                unique_history.append(conversation_history)

        return unique_history

    def generate_response(self, user_prompt):
        messages = get_conversation_history(self.key, HISTORY_SIZE)
        user_prompt = {"role": "user", "content": user_prompt}
        save_message(self.key, user_prompt)
        messages.append(user_prompt)

        unique_history = self.remove_duplicate_messages(messages)
        return unique_history

    def get_conversation_history(self, size=None):
        if not size:
            size = HISTORY_SIZE

        messages = get_conversation_history(self.key, size)

        if messages:
            unique_history = self.remove_duplicate_messages(messages)
        else:
            unique_history = list()

        return unique_history


if __name__ == "__main__":
    # system_prompt = "Welcome to the Technical Interviewer chatbot! We're here to simulate a real technical interview for a Python developer position. The role requires expertise in Django, Redis, MySQL, and AWS. I'll be asking you questions to assess your skills. Let's make this experience as authentic as possible. We'll start with an introduction:"
    system_prompt = "You are chat bot show me code"

    insert_system_prompt_if_not_exists(conversation_key, system_prompt)
    user_prompt = {"role": "user", "content": "Give me a Python code"}


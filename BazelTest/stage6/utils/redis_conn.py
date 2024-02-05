"""
Author: Hang Yan
Date created: 2023/8/9
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.

"""


import json
import redis

from config import REDIS_PORT, REDIS_HOST
# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def insert_system_prompt_if_not_exists(conversation_key, system_prompt):
    # Check if the system prompt already exists in the Redis List
    if not redis_client.lrange(conversation_key, 0, -1) or json.loads(redis_client.lindex(conversation_key, 0))['role'] != 'system':
        # Insert the system prompt at the beginning of the Redis List
        redis_client.lpush(conversation_key, json.dumps({"role": "system", "content": system_prompt}))


def message_exists(conversation_key, message):
    # Retrieve all messages in the conversation from Redis
    all_messages = redis_client.lrange(conversation_key, 0, -1)

    # Check if the message content already exists in any of the previous messages
    for stored_message in all_messages:
        stored_message = json.loads(stored_message)
        if stored_message.get('content') == message.get('content'):
            return True

    return False


def save_message(conversation_key, message):
    # Save the new message to the Redis List
    # if not message_exists(conversation_key, message):
    #     redis_client.rpush(conversation_key, json.dumps(message))
    redis_client.rpush(conversation_key, json.dumps(message))


def insert_message(conversation_key, message):
    # Save the new message to the Redis List
    redis_client.lpush(conversation_key, json.dumps(message))


def get_conversation_history(conversation_key, count):
    # Retrieve the entire conversation history from the Redis List
    if redis_client.exists(conversation_key):
        history = redis_client.lrange(conversation_key, 0, count - 1)

    else:
        history = list()
    return [json.loads(message) for message in history]

def update_latest_question(conversation_key, user_question, assistant_response):
    # Update the Redis Hash with the latest user question and assistant response
    redis_client.hset(conversation_key, "user_question", json.dumps(user_question))
    redis_client.hset(conversation_key, "assistant_response", json.dumps(assistant_response))


if __name__ == "__main__":
    # Example conversation key (use the user's identifier)
    user_identifier = "User2"
    conversation_key = f"conversation:{user_identifier}"

    # Sample messages
    system_message = {"role": "system", "content": "."}
    user_message = {"role": "user", "content": ""}
    assistant_message = {"role": "assistant", "content": ""}

    # Save user and assistant messages
    insert_message(conversation_key, system_message)
    save_message(conversation_key, user_message)
    save_message(conversation_key, assistant_message)

    # Retrieve conversation history
    conversation_history = get_conversation_history(conversation_key, 20)
    # for message in conversation_history:
    #     print(f"{message['role']}: {message['content']}")

    print(conversation_key, conversation_history)

    # Update latest user question and assistant response
    # update_latest_question(conversation_key, user_message, assistant_message)
    # latest_user_question = json.loads(redis_client.hget(conversation_key, "user_question"))
    # latest_assistant_response = json.loads(redis_client.hget(conversation_key, "assistant_response"))

    # print("\nLatest User Question:", latest_user_question['content'])
    # print("Latest Assistant Response:", latest_assistant_response['content'])

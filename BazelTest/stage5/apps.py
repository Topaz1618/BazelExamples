"""
Author: Hang Yan
Date created: 2023/8/9
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

import os
import json
from time import time, sleep

import tornado.ioloop
import tornado.web
import tornado.websocket

from utils.gpt_utils import  GptHandler
from utils.redis_conn import save_message
from dotenv import load_dotenv

load_dotenv()

from config import prompt_settings, PromptEnum
from enums import MessageType


class IndexHandler(tornado.web.RequestHandler):
    async def get(self):
        # 历史记录，基于话题和user选择
        self.gpt = GptHandler()
        self.gpt.generate_key_name(user="User1", prompt_type=PromptEnum.ChatGPT.value)
        conversation_history = self.gpt.get_conversation_history(size=100)
        print(conversation_history)

        if not conversation_history:
            conversation_history = list()

        self.render("chatbot.html", data=conversation_history)


class ChatHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        self.gpt = GptHandler()

    def on_message(self, message):
        # Process the message (e.g., call OpenAI API) and send the response back
        message = json.loads(message)
        if message["command_type"] == MessageType.COMMAND.value:
            self.gpt.generate_key_name(user="User1", prompt_type=message["payload"])
            self.gpt.init_prompt(message["payload"])

        elif message["command_type"] == MessageType.DATA.value:
            conversation_history = self.gpt.generate_response(message["payload"])
            stream = self.gpt.send_openai_request(conversation_history)

            idx = 0
            for chunk in stream:
                response = chunk["choices"][0]
                if response.get("finish_reason") == "stop":
                    print("bye bye", self.gpt.key, self.gpt.sentence)
                    save_message(self.gpt.key, {"role": "assistant", "content": self.gpt.sentence})
                    self.write_message("END MSG")
                    break

                role = response["delta"].get("role")
                content = response["delta"].get("content")
                if content:
                    if idx == 0:
                        self.write_message("START MSG")
                    print("content:", len(content), content)
                    self.gpt.sentence += content
                    self.write_message(content)
                    sleep(0.01)
                    idx += 1

    def on_close(self):
        print("WebSocket closed")


if __name__ == '__main__':
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
    }
    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/ws', ChatHandler),
    ],

        debug=True, **settings)

    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

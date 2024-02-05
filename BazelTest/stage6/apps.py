"""
Author: Hang Yan
Date created: 2023/8/9
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

import os
import json
from time import time, sleep
import os.path
import asyncio
import multiprocessing

import tornado.httpserver
import tornado.web
import tornado.options
from tornado.options import define, options
import tornado.websocket

from utils.gpt_utils import  GptHandler
from utils.redis_conn import save_message
from dotenv import load_dotenv

load_dotenv()

from config import prompt_settings, PromptEnum
from enums import MessageType
from account import RegisterHandler, LoginHandler, LogoutHandler, RestPasswordView
from base import IndexHandler
from detect_management import (CreateDetectTaskHandler, CancelDetectTaskHandler, UserDetectionTaskListHandler,
                               DetectTaskProgressHandler, WsDetectTaskProgressHandler, WsDetectStatusUpdateHandler,
                               UploadDetectFileHandler, SingleDetectionTaskHandler)
from task_queue_listener import my_process

define("port", default=8888, help="run on the given port", type=int)


def process_function():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_process())



class GPTHandler(tornado.web.RequestHandler):
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
        print(message["command_type"] )
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
    tornado.options.parse_command_line()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
    }
    application = tornado.web.Application([
        (r'/register', RegisterHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r'/reset_password', RestPasswordView),

        (r'/', IndexHandler),
        (r'/chat', GPTHandler),

        (r'/detect/create_task', CreateDetectTaskHandler),
        (r'/detect/cancel_task', CancelDetectTaskHandler),
        (r'/detect/upload', UploadDetectFileHandler),
        (r'/detect/progress/([^/]+)', DetectTaskProgressHandler),
        (r'/detect/wsprogress', WsDetectTaskProgressHandler),
        (r'/detect/ws_status_update', WsDetectStatusUpdateHandler),
        (r'/get_tasks', UserDetectionTaskListHandler),
        (r'/single_detection_task', SingleDetectionTaskHandler),

        (r'/ws', ChatHandler),
    ],

        debug=True, **settings)
    try:
        loop = asyncio.get_event_loop()
        # asyncio.gather(listen_idle_detect_task_workers(application))
        # task = asyncio.create_task(listen_idle_detect_task_workers(application))
        process = multiprocessing.Process(target=process_function)
        process.start()
        print("Async task process started")

        # Create an HTTP server instance
        http_server = tornado.httpserver.HTTPServer(
            application,
            # ssl_options=context,
            max_buffer_size=10485760000)

        # Listen on the specified port
        http_server.listen(options.port)
        print("server start")

        # Start the event loop
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt as e:
        print("Quit")

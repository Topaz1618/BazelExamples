import uuid
import json
import asyncio
from time import time, sleep
from datetime import datetime


import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket

from base import BaseHandler
from rpc_client import rpc_client_conn
from task_utils import (get_task_info, create_task, update_task_info,  add_detect_task_to_queue,
                        remove_task_from_detect_queue, get_task_status_lists, get_available_nodes)
from account_utils import (get_token_user, get_account_info, admin_login_redirect, async_admin_login_redirect,
                           auth_login_redirect, async_auth_login_redirect)
from file_utils import generate_detect_file_gridfs_save_name
from extensions import UserManager, ModelsManager, DatasetsManager, AsyncGridFSManager, DetectionFileManager, DetectionTaskManager
from enums import TaskType, TaskStatus, TaskInfoKey, UploadStatus
from config import detect_nodes, RPC_PORT


class WsDetectStatusUpdateHandler(tornado.websocket.WebSocketHandler):
    def _send_progress(self, loop):
        asyncio.set_event_loop(loop)
        while True:
            nodes = get_available_nodes(TaskType.DETECT.value)
            complete_task_list, pending_task_list, processing_task_list = get_task_status_lists(TaskType.DETECT.value)

            data = {
                "nodes": nodes,
                # "complete_task_list": complete_task_list,
                "pending_task_list": pending_task_list,
                "processing_task_list": processing_task_list,
            }
            # print(data)

            self.write_message(json.dumps(data))

            sleep(5)

    async def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        # Process the message (e.g., call OpenAI API) and send the response back

        # task_id = message["task_id"]
        loop = asyncio.get_event_loop()
        asyncio.gather(loop.run_in_executor(None, self._send_progress, loop), )


    def on_close(self):
        print("WebSocket closed")


class DetectTaskProgressHandler(BaseHandler):
    def get(self, task_id):
        print(task_id)
        task_info = get_task_info(task_id)
        processed_file_count = task_info.get("processed_file_count", 0)
        total_file_count = task_info.get("total_file_count", 1)
        progress = round(int(processed_file_count) / int(total_file_count) * 100, 2)

        self.render("detect_progress.html", task_id=task_id, task_info=task_info, progress=progress)


class WsDetectTaskProgressHandler(tornado.websocket.WebSocketHandler):
    def _send_progress(self, task_id, loop):
        asyncio.set_event_loop(loop)
        while True:
            task_info = get_task_info(task_id)
            if not task_info:
                continue

            processed_file_count = task_info.get("processed_file_count", 0)
            total_file_count = task_info.get("total_file_count", 1)
            print(task_info)

            if task_info.get("status") == TaskStatus.COMPLETED.value:
                data = {
                    "log": task_info.get("log", ["waiting..."])[-1],
                    "progress": 100,
                    "status": TaskStatus.COMPLETED.value,
                    "res": json.dumps(task_info.get("res", {})),
                }
                self.write_message(json.dumps(data))
                break

            progress = round(int(processed_file_count) / int(total_file_count) * 100, 2)
            data = {
                "log": task_info.get("log", [f"Task ID: [{task_id}] is still waiting...",])[-1],
                "progress": progress,
                "status": task_info.get("status"),
            }
            self.write_message(json.dumps(data))

            sleep(1)

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        # Process the message (e.g., call OpenAI API) and send the response back
        message = json.loads(message)

        task_id = message["task_id"]
        loop = asyncio.get_event_loop()

        asyncio.gather(loop.run_in_executor(None, self._send_progress, task_id, loop), )

        print(f"Task ID: {task_id}")

    def on_close(self):
        print("WebSocket closed")


class CreateDetectTaskHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        model_manager = ModelsManager()
        models_count = model_manager.get_models_count(username, is_admin=is_admin)
        model_list = model_manager.get_models(0, models_count, username, is_admin)

        self.render("create_detect_task.html", username=username, account_name=account_name, is_admin=is_admin, model_list=model_list)

    @auth_login_redirect
    def post(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        model = self.get_argument('detect_model')

        detect_file_obj = self.request.files.get('detect_file')
        if not detect_file_obj:
            self.write({'status': 'failed', "message": "Detect file does not exists"})
            return

        detect_file_name = detect_file_obj[0]['filename']
        # detect_file_name = 'detect_demo1.zip'

        task_id = str(uuid.uuid4())  # 生成唯一的任务ID
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(task_id, create_time, model, detect_file_name)
        task_info = create_task(task_id, TaskType.DETECT.value, create_time, model, detect_file_name)
        add_detect_task_to_queue(task_id)

        task_obj = DetectionTaskManager()
        task_obj.create_task(task_id, username, model, detect_file_name, create_time)
        task_obj.close()

        self.set_status(200)
        self.write({'status': 'success', 'message': {"task_id": task_id}})


class CancelDetectTaskHandler(BaseHandler):
    async def post(self):
        """
        处理取消任务的逻辑

        :param task_id: Unique ID of task

        :return:
            Success:
                {"Task ID": "","error_code": "1000"}
            Failed:
                {"Task ID": "", "error_code": ""}
        """

        task_id = self.get_argument('task_id')
        task_info = get_task_info(task_id)
        task_pid = task_info.get("task_pid")
        task_node = task_info.get("node")
        task_status = task_info.get("status")

        if task_status == TaskStatus.IN_PROGRESS.value:
            task_node_ip = detect_nodes[task_node]["ip"]

            print("!!!!!", task_pid, task_node, task_node_ip)

            client = await rpc_client_conn(task_node_ip, RPC_PORT)
            res = await client.call("stop_worker", task_id, task_pid, task_node, TaskType.DETECT.value)

        elif task_status == TaskStatus.PENDING.value:
            remove_task_from_detect_queue(task_id)
            update_task_info(task_id, TaskInfoKey.STATUS.value, TaskStatus.CANCELLED.value)
            update_task_info(task_id, TaskInfoKey.LOG.value, "Task has been canceled")

        else:
            raise ValueError("wrong TaskStatus type ")

        self.write({"error_msg": "success", "error_code": 1000})


class UploadDetectFileHandler(BaseHandler):
    @async_auth_login_redirect
    async def post(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        chunk_number = int(self.request.headers.get('X-Chunk-Number'))
        filename = self.get_argument("filename", None)
        task_id = self.get_argument("task_id", None)
        file_size = self.get_argument("file_size", None)
        total_chunks = self.get_argument("chunks", None)
        if not isinstance(total_chunks, int):
            total_chunks = int(total_chunks)

        print(f"filename: {filename} Task ID: {task_id} Chunk Number: {chunk_number} {type(chunk_number)} Total chunks: {total_chunks} {type(total_chunks)}")
        chunk_data = self.request.files["file"][0]["body"]
        print("chunk data len:",  len(chunk_data))

        async_gridfs_obj = AsyncGridFSManager()
        save_name = generate_detect_file_gridfs_save_name(filename, task_id)

        await async_gridfs_obj.upload_chunk(chunk_data, save_name)

        if chunk_number == 1:
            detection_file_obj = DetectionFileManager()
            created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            detection_file_obj.create_file(filename, task_id, username, total_chunks, created_time)
            detection_file_obj.update_file_status(filename, task_id, "num", chunk_number)

        if chunk_number == total_chunks:
            detection_file_obj = DetectionFileManager()
            detection_file_obj.update_file_status(filename, task_id, "num", chunk_number)
            detection_file_obj.update_file_status(filename, task_id, "upload_status", UploadStatus.COMPLETED.value)

        self.set_status(200)
        self.write({'status': 'success', 'message': '模型上传成功。'})


class GetModelsHandler(BaseHandler):
    def get(self):
        """
        获取所有可用模型

        :return:
            Success:
                [{"model_name": "", "version": ""}, {"model_name": "", "version": ""}, ]
            Failed:
                {"error_message": "", "error_code": ""}
        """

        pass


class UserDetectionTaskListHandler(BaseHandler):
    @async_auth_login_redirect
    async def get(self):
        # 处理获取数据集管理的逻辑
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        task_obj = DetectionTaskManager()
        task_count = task_obj.get_tasks_count(username, is_admin)
        task_list = task_obj.get_tasks(0, task_count, username, is_admin, is_personal=True)

        self.render("user_detection_tasks.html", username=username, account_name=account_name, is_admin=is_admin, task_list=task_list)


class SingleDetectionTaskHandler(BaseHandler):
    @async_auth_login_redirect
    async def get(self):
        # 处理获取数据集管理的逻辑
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)
        task_id = self.get_argument("task_id", None)

        task_obj = DetectionTaskManager()

        task_info = task_obj.get_task(task_id)
        result = task_info["res"]
        # self.render("user_models.html", data=data_list)
        self.render("single_detection_task.html", username=username, account_name=account_name, is_admin=is_admin, task_id=task_id, task_result=result)

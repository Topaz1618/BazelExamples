"""
Author: Hang Yan
Date created: 2023/8/13
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""
import os
from dotenv import load_dotenv

ENV = 'DEV'

if ENV == 'DEV':
    from config_dev import *
    env_file = '.env_dev'

elif ENV == 'PROD':
    from config_prod import *
    env_file = '.env_prod'

print(env_file)
load_dotenv(env_file)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_SERVERS = [
    f'{MONGODB_HOST}:30001',
    f'{MONGODB_HOST}:30002',
    f'{MONGODB_HOST}:30003',
]

RPC_PORT = 4000

replicaSet = os.getenv("replicaSet")
FileSystem = os.getenv("FileSystem")
GRIDFS_COLLECTION_NAME = os.getenv("GRIDFS_COLLECTION_NAME")

SECRET = os.getenv("SECRET").encode()
SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_TIMEOUT = 3600 * 1000 * 24

detect_nodes = {
    "detect_node1": {
        "ip": "127.0.0.1",
        "capacity": 2,  # 初始能力数值为1
    },
}


# Training任务处理节点
training_nodes = {
    "training_node1": {
        # "ip": "81.71.15.27",
        "ip": "134.175.73.72",
        "capacity": 2,  # 初始能力数值为1
    },
    "training_node2": {
        "ip": "134.175.73.72",
        "capacity": 0,  # 初始能力数值为1
    },
}


USED_DETECT_NODES = "used_detect_nodes"
USED_TRAINING_NODES = "used_training_nodes"
DETECT_TASK_QUEUE = "detect_task_queue"
TRAINING_TASK_QUEUE = "training_task_queue"
TASK_DICT = "task_dict"

import asyncio
import aio_msgpack_rpc
import argparse
from enum import Enum
from time import sleep, time
from config import RPC_PORT

# 创建参数解析器
parser = argparse.ArgumentParser(description='Description of your script')

# 添加需要的参数
parser.add_argument('--manage_type', type=int, help='kill pid')
parser.add_argument('--pid', type=int, help='kill pid',  nargs='?')

# 解析命令行参数
args = parser.parse_args()


# WORKER_IP = "127.0.0.1"  # 替换成真正的 worker IP
# RPC_PORT = 4000


class TaskManagementTypeEnum(Enum):
    START = 1
    STOP = 2


async def rpc_client_conn(worker_ip, worker_port=4000):
    try:
        # print("!!!!!", worker_ip, worker_port)
        reader, writer = await asyncio.open_connection(worker_ip, worker_port)
        client = aio_msgpack_rpc.Client(reader, writer)
        return client
    except Exception as e:
        raise Exception("Failed to connect to RPC server:", str(e))


# async def main():
#     try:
#         client = await rpc_client_conn(WORKER_IP, RPC_PORT)
#         task_type = 2
#         if args.manage_type == TaskManagementTypeEnum.START.value:
#             task_info = {"command": "python detect.py", "task_id": "2"}
#             res = await client.call("start_worker", task_type, task_info)
#             print("PID:", res)
#
#         elif args.manage_type == TaskManagementTypeEnum.STOP.value:
#             res2 = await client.call("stop_worker", task_type, args.pid)
#             print(res2)
#
#     except Exception as e:
#         print("Error:", str(e))
#     finally:
#         print("success")
#         client.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
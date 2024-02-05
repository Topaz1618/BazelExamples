"""
分布式任务的监听

"""

import requests
import json
import logging
from time import sleep
import redis


from task_utils import (generate_task_command, get_task_from_detect_queue, remove_task_from_detect_queue,
                        add_used_capacity, remove_task_from_training_queue, get_task_from_training_queue,
                        update_task_info)


from enums import TaskType, TaskInfoKey
from rpc_client import rpc_client_conn
from config import (detect_nodes, training_nodes, RPC_PORT, USED_DETECT_NODES, USED_TRAINING_NODES,
                    REDIS_HOST, REDIS_PORT)
from log_handler import logger

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def get_available_node(used_capacity, total_nodes):
    used_capacity = used_capacity if used_capacity else {}

    # from ipdb import set_trace; set_trace()


    if not used_capacity:
        for node, capacity_info in total_nodes.items():
            if capacity_info["capacity"] > 0:
                return node

    for node, capacity in total_nodes.items():
        # print(node, capacity, used_capacity)
        node_capacity_info = used_capacity.get(node.encode(), {})
        if isinstance(node_capacity_info, bytes):
            node_capacity_info = node_capacity_info.decode()

        if isinstance(node_capacity_info, str):
            node_capacity_info = json.loads(node_capacity_info)

        used_capacity_num = node_capacity_info.get("cap_num", 0)

        available_capacity_num = capacity["capacity"] - used_capacity_num

        if available_capacity_num > 0:
            return node



async def listen_idle_detect_task_workers():
    idx = 0
    while True:
        sleep(2)
        idx += 1

        used_detect_nodes = redis_client.hgetall(USED_DETECT_NODES)
        idle_detect_node = get_available_node(used_detect_nodes, detect_nodes)

        used_training_nodes = redis_client.hgetall(USED_TRAINING_NODES)
        idle_training_node = get_available_node(used_training_nodes, training_nodes)

        if idx % 2 == 0:
            logger.debug(f"Detection Node: Used [{used_detect_nodes if used_detect_nodes else 'None'}] | Idle [{idle_detect_node}]")
            logger.debug(f"Training Node: Used [{used_training_nodes if used_training_nodes else 'None'}] | Idle [{idle_training_node}]")

        # ForkedPdb().set_trace()
        if idle_detect_node:
            rpc_server_ip = detect_nodes.get(idle_detect_node, {}).get("ip", None)

            task_id = get_task_from_detect_queue()
            if task_id and rpc_server_ip:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_detect_node, TaskType.DETECT.value)

                logger.info(f"Initiating Detection Process: Task ID: [{task_id}], Command: {command}")
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_detect_node)

                task_info = {"task_id": task_id, "command": command}
                # ForkedPdb().set_trace()

                res = await client.call("start_worker", task_id, idle_detect_node, TaskType.DETECT.value, task_info)
                # ForkedPdb().set_trace()
                add_used_capacity(idle_detect_node, TaskType.DETECT.value)
                remove_task_from_detect_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Detection Task Started Successfully: Task ID: [{task_id}], Detection Node: {idle_detect_node}")
            else:
                logger.debug("Detection Queue: No tasks in the queue")

        # ForkedPdb().set_trace()
        if idle_training_node:

            rpc_server_ip = training_nodes.get(idle_training_node, {}).get("ip", None)
            print("!!", idle_training_node, rpc_server_ip, )
            task_id = get_task_from_training_queue()
            if task_id:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_training_node, TaskType.TRAINING.value)

                logger.info(f"Initiating Training Process: Task ID: [{task_id}], Command: {command}")

                task_info = {"task_id": task_id, "command": command}
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_training_node)

                res = await client.call("start_worker", task_id, idle_training_node, TaskType.TRAINING.value, task_info)

                add_used_capacity(idle_training_node, TaskType.TRAINING.value)
                remove_task_from_training_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Training Task Started Successfully: Task ID: [{task_id}], Training Node: {idle_training_node}")
            else:
                logger.debug("Training Queue: No tasks in the queue")


async def listen_idle_training_task_workers():
    idx = 0
    while True:
        sleep(2)
        idx += 1

        used_detect_nodes = redis_client.hgetall(USED_DETECT_NODES)
        idle_detect_node = get_available_node(used_detect_nodes, detect_nodes)

        used_training_nodes = redis_client.hgetall(USED_TRAINING_NODES)
        idle_training_node = get_available_node(used_training_nodes, training_nodes)

        if idx % 2 == 0:
            logger.debug(f"Detection Node: Used [{used_detect_nodes if used_detect_nodes else 'None'}] | Idle [{idle_detect_node}]")
            logger.debug(f"Training Node: Used [{used_training_nodes if used_training_nodes else 'None'}] | Idle [{idle_training_node}]")

        # ForkedPdb().set_trace()
        if idle_detect_node:
            rpc_server_ip = detect_nodes.get(idle_detect_node, {}).get("ip", None)

            task_id = get_task_from_detect_queue()
            if task_id and rpc_server_ip:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_detect_node, TaskType.DETECT.value)

                logger.info(f"Initiating Detection Process: Task ID: [{task_id}], Command: {command}")
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_detect_node)

                task_info = {"task_id": task_id, "command": command}
                # ForkedPdb().set_trace()

                res = await client.call("start_worker", task_id, idle_detect_node, TaskType.DETECT.value, task_info)
                # ForkedPdb().set_trace()
                add_used_capacity(idle_detect_node, TaskType.DETECT.value)
                remove_task_from_detect_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Detection Task Started Successfully: Task ID: [{task_id}], Detection Node: {idle_detect_node}")
            else:
                logger.debug("Detection Queue: No tasks in the queue")

        # ForkedPdb().set_trace()
        if idle_training_node:

            rpc_server_ip = training_nodes.get(idle_training_node, {}).get("ip", None)
            # print("!!", idle_training_node, rpc_server_ip, )
            task_id = get_task_from_training_queue()
            if task_id:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_training_node, TaskType.TRAINING.value)

                logger.info(f"Initiating Training Process: Task ID: [{task_id}], Command: {command}")

                task_info = {"task_id": task_id, "command": command}
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_training_node)

                res = await client.call("start_worker", task_id, idle_training_node, TaskType.TRAINING.value, task_info)

                add_used_capacity(idle_training_node, TaskType.TRAINING.value)
                remove_task_from_training_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Training Task Started Successfully: Task ID: [{task_id}], Training Node: {idle_training_node}")
            else:
                logger.debug("Training Queue: No tasks in the queue")



async def my_process():
    idx = 0
    while True:
        sleep(2)
        idx += 1

        used_detect_nodes = redis_client.hgetall(USED_DETECT_NODES)
        idle_detect_node = get_available_node(used_detect_nodes, detect_nodes)

        used_training_nodes = redis_client.hgetall(USED_TRAINING_NODES)
        idle_training_node = get_available_node(used_training_nodes, training_nodes)

        if idx % 2 == 0:
            logger.debug(f"Detection Node: Used [{used_detect_nodes if used_detect_nodes else 'None'}] | Idle [{idle_detect_node}]")
            logger.debug(f"Training Node: Used [{used_training_nodes if used_training_nodes else 'None'}] | Idle [{idle_training_node}]")

        # ForkedPdb().set_trace()
        if idle_detect_node:
            rpc_server_ip = detect_nodes.get(idle_detect_node, {}).get("ip", None)

            task_id = get_task_from_detect_queue()
            if task_id and rpc_server_ip:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_detect_node, TaskType.DETECT.value)

                logger.info(f"Initiating Detection Process: Task ID: [{task_id}], Command: {command}")
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_detect_node)

                task_info = {"task_id": task_id, "command": command}
                # ForkedPdb().set_trace()

                res = await client.call("start_worker", task_id, idle_detect_node, TaskType.DETECT.value, task_info)
                # ForkedPdb().set_trace()
                add_used_capacity(idle_detect_node, TaskType.DETECT.value)
                remove_task_from_detect_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Detection Task Started Successfully: Task ID: [{task_id}], Detection Node: {idle_detect_node}")
            else:
                logger.debug("Detection Queue: No tasks in the queue")

        # ForkedPdb().set_trace()
        if idle_training_node:

            rpc_server_ip = training_nodes.get(idle_training_node, {}).get("ip", None)
            # print("!!", idle_training_node, rpc_server_ip, )
            task_id = get_task_from_training_queue()
            if task_id:
                client = await rpc_client_conn(rpc_server_ip, RPC_PORT)
                command = generate_task_command(task_id, idle_training_node, TaskType.TRAINING.value)

                logger.info(f"Initiating Training Process: Task ID: [{task_id}], Command: {command}")

                task_info = {"task_id": task_id, "command": command}
                update_task_info(task_id, TaskInfoKey.NODE.value, idle_training_node)

                res = await client.call("start_worker", task_id, idle_training_node, TaskType.TRAINING.value, task_info)

                add_used_capacity(idle_training_node, TaskType.TRAINING.value)
                remove_task_from_training_queue(task_id)

                if res["error_code"] == "1000":
                    logger.info(f"Training Task Started Successfully: Task ID: [{task_id}], Training Node: {idle_training_node}")
            else:
                logger.debug("Training Queue: No tasks in the queue")

import uuid
import redis
import json

from time import time, sleep
from datetime import datetime


from enums import TaskType, TaskStatus, WorkerConnectionStatus, TaskKeyType
from config import (USED_DETECT_NODES, USED_TRAINING_NODES, DETECT_TASK_QUEUE, TRAINING_TASK_QUEUE,
                    detect_nodes, training_nodes, REDIS_HOST, REDIS_PORT)

# 连接到 Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


# 添加任务到任务队列
def add_training_task_to_queue(task_id):
    redis_client.rpush(TRAINING_TASK_QUEUE, task_id)


def add_detect_task_to_queue(task_id):
    redis_client.rpush(DETECT_TASK_QUEUE, task_id)


def get_task_from_detect_queue():
    task_id = redis_client.lindex(DETECT_TASK_QUEUE, 0)
    if isinstance(task_id, bytes):
        task_id = task_id.decode()
    return task_id


def remove_task_from_detect_queue(task_id):
    removed_count = redis_client.lrem(DETECT_TASK_QUEUE, 0, task_id)
    print("Removed count:", removed_count)
    return removed_count


def get_task_from_training_queue():
    task_id = redis_client.lindex(TRAINING_TASK_QUEUE, 0)
    return task_id


def remove_task_from_training_queue(task_id):
    removed_count = redis_client.lrem(TRAINING_TASK_QUEUE, 0, task_id)
    print("Removed count:", removed_count)
    return removed_count


def get_task_status_lists(task_type):
    task_dict_data = redis_client.hgetall("task_dict")

    # Check if the task status is 1
    complete_task_list = list()
    pending_task_list = list()
    processing_task_list = list()

    # Iterate over the task data
    for task_id, task_data in task_dict_data.items():
        # Convert the task data from bytes to a string
        task_data_str = task_data.decode("utf-8")

        # Parse the task data as a JSON object
        task = json.loads(task_data_str)

        if isinstance(task_id, bytes):
            task_id = task_id.decode()

        if task["status"] == TaskStatus.COMPLETED.value and task["task_type"] == task_type:
            # Perform actions on the task with status 1
            complete_task_list.append({"task_id": task_id, "status": task["status"], "create_time": task.get("create_time")})

        elif task["status"] == TaskStatus.PENDING.value and task["task_type"] == task_type:
            # Perform actions on the task with status 1
            pending_task_list.append({"task_id": task_id, "status": task["status"],  "create_time": task.get("create_time")})

        elif task["status"] == TaskStatus.IN_PROGRESS.value and task["task_type"] == task_type:
            # Perform actions on the task with status 1
            processing_task_list.append({"task_id": task_id, "status": task["status"], "node": task.get("node"), "create_time": task.get("create_time")})

        else:
            continue

    # print(complete_task_list, pending_task_list, processing_task_list)
    return complete_task_list, pending_task_list, processing_task_list


def get_available_nodes(task_type):
    if task_type == TaskType.DETECT.value:
        used_capacity = redis_client.hgetall(USED_DETECT_NODES)
        total_nodes = detect_nodes

    elif task_type == TaskType.TRAINING.value:
        used_capacity = redis_client.hgetall(USED_TRAINING_NODES)
        total_nodes = training_nodes

    else:
        raise ValueError("check task type")

    available_nodes = list()
    used_capacity = used_capacity if used_capacity else {}

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
            available_nodes.append({"node": node, "capacity_num": available_capacity_num})

    print(available_nodes)
    return available_nodes


def add_used_capacity(node, task_type):
    if not isinstance(node, bytes):
        node = node.encode()

    if task_type == TaskType.DETECT.value:
        used_node_key = USED_DETECT_NODES

    elif task_type == TaskType.TRAINING.value:
        used_node_key = USED_TRAINING_NODES

    else:
        raise ValueError("wrong task type")

    if redis_client.hexists(used_node_key, node):
        existing_value = redis_client.hget(used_node_key, node)
        print(existing_value)
        existing_value_dict = json.loads(existing_value.decode('utf-8'))
        # 检查字典中是否有'cap_num'键
        if 'cap_num' in existing_value_dict:
            # 如果有'cap_num'键，将其值加1
            existing_value_dict['cap_num'] += 1
        else:
            # 如果没有'cap_num'键，创建'cap_num'键并设置为1
            existing_value_dict['cap_num'] = 1

        redis_client.hset(used_node_key, node, json.dumps(existing_value_dict))

        print(redis_client.hgetall(used_node_key))
    else:

        redis_client.hset(used_node_key, node, json.dumps({'cap_num': 1}))


def remove_used_capacity(node, task_type):
    if not isinstance(node, bytes):
        node = node.encode()

    if task_type == TaskType.DETECT.value:
        used_node_key = USED_DETECT_NODES

    elif task_type == TaskType.TRAINING.value:
        used_node_key = USED_TRAINING_NODES

    else:
        raise ValueError("wrong task type")
    print("!!!node key", used_node_key)

    if redis_client.hexists(used_node_key, node):
        existing_value = redis_client.hget(used_node_key, node)
        print(existing_value)

        existing_value_dict = json.loads(existing_value.decode('utf-8'))
        # 检查字典中是否有'cap_num'键
        if 'cap_num' in existing_value_dict and existing_value_dict['cap_num'] >= 1:
            # 如果有'cap_num'键，将其值加1
            existing_value_dict['cap_num'] -= 1
        else:
            # 如果没有'cap_num'键，创建'cap_num'键并设置为1
            print("There's no key called cap_num")

        redis_client.hset(used_node_key, node, json.dumps(existing_value_dict))

        print(redis_client.hgetall(used_node_key))
    else:
        print("a节点不存在")


def create_training_command(task_id, node, model, dataset, epoch, batch_size, learning_rate):
    if isinstance(task_id, bytes):
        task_id = task_id.decode()

    command = f"python train.py --task_id {task_id} --node {node} --model {model} --dataset {dataset} --epoch {epoch} " \
              f"--batch_size {batch_size} --learning_rate {learning_rate}"

    return command


def create_detect_command(task_id, model, node):
    if isinstance(task_id, bytes):
        task_id = task_id.decode()

    command = f"python detect.py --task_id {task_id} --model {model} --node {node}"
    return command


# 获取任务详情
def get_task_info(task_id):
    if not isinstance(task_id, bytes):
        task_id = task_id.encode()

    task_info = dict()

    task = redis_client.hget('task_dict', task_id)
    if task:
        task_info = json.loads(task)
    return task_info


def update_task_info(task_id, key, value):
    if not isinstance(task_id, bytes):
        task_id = task_id.encode()

    # from ipdb import set_trace; set_trace()
    task_dict = redis_client.hgetall('task_dict')
    if task_id in task_dict:
        task_info = json.loads(task_dict[task_id])

        if key == TaskKeyType.LOG.value:
            log_info = task_info.get(key, [])  # 获取现有的日志列表，如果不存在则创建一个空列表
            log_info.append(value)  # 将新的日志消息追加到列表中
            task_info[key] = log_info
            redis_client.hset('task_dict', task_id.decode(), json.dumps(task_info))

        else:
            task_info[key] = value
            redis_client.hset('task_dict', task_id.decode(), json.dumps(task_info))


def delete_task_key(task_id, key):
    if not isinstance(task_id, bytes):
        task_id = task_id.encode()

    task_dict = redis_client.hgetall('task_dict')
    if task_id in task_dict:
        task_info = json.loads(task_dict[task_id])

        if key in task_info:
            del task_info[key]
            redis_client.hset('task_dict', task_id, json.dumps(task_info))


def create_task(task_id, task_type,  create_time, *kwargs):
    task = {
        'task_id': task_id,
        'status': TaskStatus.PENDING.value,
        'create_time': create_time,
        'task_type': task_type,
    }

    if task_type == TaskType.DETECT.value:
        model, detect_file = kwargs
        task['model'] = model
        task['detect_file'] = detect_file

    elif task_type == TaskType.TRAINING.value:
        # from ipdb import set_trace; set_trace()
        model, dataset, epoch, batch_size, learning_rate = kwargs
        task['model'] = model
        task['dataset'] = dataset
        task['epoch'] = epoch
        task['batch_size'] = batch_size
        task['learning_rate'] = learning_rate

    else:
        raise Exception("Invalid task type")

    json_task = json.dumps(task)
    redis_client.hset('task_dict', task_id, json_task)
    return json_task


# 从任务队列获取任务并处理
def generate_detect_task_command(task_id, node):
    # task_id = redis_client.lindex('detect_task_queue', 0)
    # remove_task_id = redis_client.lpop('detect_task_queue')

    # 获取任务详情
    task_info = get_task_info(task_id)
    if task_info:
        model = task_info['model']
        # 处理任务的逻辑
        command = create_detect_command(task_id, model, node)
        return command
    else:
        print(f"No details found for task ID: {task_id}")
        return None

# 从任务队列获取任务并处理
def generate_training_task_command(task_id, node):
    task_info = get_task_info(task_id)
    if task_info:
        model = task_info['model']
        dataset = task_info['dataset']
        epoch = task_info['epoch']
        batch_size = task_info['batch_size']
        learning_rate = task_info['learning_rate']


        # # 更新任务状态为 1 (处理中)
        # update_task_info(task_id, "status", TaskStatus.IN_PROGRESS.value)
        #
        # # 更新上次 worker 连接时间
        # last_updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # update_task_info(task_id, "last_updated_time", last_updated_time)
        #
        # # 更新Worker 连接状态
        # update_task_info(task_id, "work_conn_status", WorkerConnectionStatus.CONNECTING.value)

        # 处理任务的逻辑

        command = create_training_command(task_id, node, model, dataset, epoch, batch_size, learning_rate)
        return command
    else:
        print(f"No details found for task ID: {task_id}")
        return None


def generate_task_command(task_id, node, task_type):
    if task_type == TaskType.DETECT.value:

        res = generate_detect_task_command(task_id, node)

    elif task_type == TaskType.TRAINING.value:
        res = generate_training_task_command(task_id, node)

    else:
        raise ValueError("invalid parameters")

    return res





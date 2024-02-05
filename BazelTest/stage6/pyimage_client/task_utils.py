import os
import uuid
import redis
import random
import json
import shutil
from time import time, sleep
from datetime import datetime
from collections import OrderedDict

import pdfplumber
import pytesseract
import cv2
import numpy as np

from enums import TaskType, TaskStatus, WorkerConnectionStatus, TaskKeyType, TaskInfoKey, MaterialContentType, MaterialType
from config import (USED_DETECT_NODES, USED_TRAINING_NODES, DETECT_TASK_QUEUE, TRAINING_TASK_QUEUE,
                    REDIS_HOST, REDIS_PORT)
from log_handler import logger

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True, readonly=False)


def add_training_task_to_queue(task_id):
    redis_client.rpush(TRAINING_TASK_QUEUE, task_id)


def add_detect_task_to_queue(task_id):
    redis_client.rpush(DETECT_TASK_QUEUE, task_id)


def get_task_from_detect_queue():
    task_id = redis_client.lindex(DETECT_TASK_QUEUE, 0)
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


def get_idle_workers(used_capacity, total_nodes):
    used_capacity = used_capacity if used_capacity else {}

    if not used_capacity:
        for node, capacity_info in total_nodes.items():
            if capacity_info["capacity"] > 0:
                return node

    for node, capacity in total_nodes.items():
        used_capacity = used_capacity.get(node.encode(), {})
        if isinstance(used_capacity, bytes):
            used_capacity = used_capacity.decode()

        if isinstance(used_capacity, str):
            used_capacity = json.loads(used_capacity)

        used_capacity_num = used_capacity.get("cap_num", 0)
        print("used_capacity_num", used_capacity_num)
        available_capacity_num = capacity["capacity"] - used_capacity_num

        if available_capacity_num > 0:
            return node


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

        if 'cap_num' in existing_value_dict:
            existing_value_dict['cap_num'] += 1
        else:
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

    if redis_client.hexists(used_node_key, node):
        existing_value = redis_client.hget(used_node_key, node)
        print(existing_value)

        existing_value_dict = json.loads(existing_value.decode('utf-8'))
        if 'cap_num' in existing_value_dict and existing_value_dict['cap_num'] >= 1:
            existing_value_dict['cap_num'] -= 1
        else:
            print("There's no key called cap_num")

        if existing_value_dict['cap_num'] == 0:
            redis_client.hdel(used_node_key, node)
        else:
            redis_client.hset(used_node_key, node, json.dumps(existing_value_dict))

        print(redis_client.hgetall(used_node_key))
    else:
        print("节点不存在")


def create_training_command(task_id, node, model, dataset, epoch, weight, batch_size, learning_rate, activation_function):
    if isinstance(task_id, bytes):
        task_id = task_id.decode()

    command = f"python train.py --task_id {task_id} --node {node} --model {model} --dataset {dataset} --epoch {epoch} " \
              f"--weight {weight} --batch_size {batch_size} --learning_rate {learning_rate} " \
              f"--activation_function {activation_function}"

    return command


def create_detect_command(task_id, model, node):
    if isinstance(task_id, bytes):
        task_id = task_id.decode()

    command = f"python detect.py --task_id {task_id} --model {model} --node {node}"
    return command


def get_task_info(task_id):
    if not isinstance(task_id, bytes):
        task_id = task_id.encode()

    task_info = None

    task_dict = redis_client.hgetall('task_dict')
    task = task_dict.get(task_id)
    if task:
        task_info = json.loads(task)

    return task_info


def update_task_info(task_id, key, value):

    if not isinstance(task_id, bytes):
        task_id = task_id.encode()

    task_info = redis_client.hget('task_dict', task_id)
    if task_info:
        task_info = json.loads(task_info)

    if key == TaskKeyType.LOG.value:
        log_info = task_info.get(key, [])
        log_info.append(value)
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



def generate_detect_task_command(task_id, node):
    # task_id = redis_client.lindex('detect_task_queue', 0)
    # remove_task_id = redis_client.lpop('detect_task_queue')

    task_info = get_task_info(task_id)
    if task_info:
        model = task_info['model']
        update_task_info(task_id, TaskInfoKey.STATUS.value, TaskStatus.IN_PROGRESS.value)
        last_updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_task_info(task_id, TaskInfoKey.LAST_UPDATED_TIME.value, last_updated_time)
        update_task_info(task_id, TaskInfoKey.WORK_CONN_STATUS.value, WorkerConnectionStatus.CONNECTING.value)
        command = create_detect_command(task_id, model, node)
        return command
    else:
        print(f"No details found for task ID: {task_id}")
        return None

def generate_training_task_command(task_id, node):
    print(task_id)

    task_info = get_task_info(task_id)

    if task_info:
        model = task_info['model']
        dataset = task_info['dataset']
        epoch = task_info['epoch']
        weight = task_info['weight']
        batch_size = task_info['batch_size']
        learning_rate = task_info['learning_rate']
        activation_function = task_info['activation_function']

        update_task_info(task_id, "status", TaskStatus.IN_PROGRESS.value)
        last_updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_task_info(task_id, TaskInfoKey.LAST_UPDATED_TIME.value, last_updated_time)
        update_task_info(task_id, TaskInfoKey.WORK_CONN_STATUS.value, WorkerConnectionStatus.CONNECTING.value)

        command = create_training_command(task_id, node, model, dataset, epoch, weight, batch_size, learning_rate, activation_function)
        return command
    else:
        print(f"No details found for task ID: {task_id}")
        return None


class MaterialFactory:
    @staticmethod
    def create_material_type(value):
        return MaterialType.from_string(value)


def detect_material_type(ocr_text):
    material_type_mapping = OrderedDict([
        (MaterialContentType.INTEGRATION_OF_RURAL_HOUSING_AND_LAND.value, MaterialType.INTEGRATION_OF_RURAL_HOUSING_AND_LAND.value),
        (MaterialContentType.BOUNDARY_NOTIFICATION.value, MaterialType.BOUNDARY_NOTIFICATION.value),
        ((MaterialContentType.REAL_ESTATE_APPLICATION.value, MaterialContentType.REAL_ESTATE_APPLICATION1.value),
         MaterialType.REAL_ESTATE_APPLICATION.value),
        ((MaterialContentType.PUBLIC_NOTICE_OF_NO_OBJECTION.value, MaterialContentType.PUBLIC_NOTICE_OF_NO_OBJECTION2.value), MaterialType.PUBLIC_NOTICE_OF_NO_OBJECTION.value),
        (MaterialContentType.DEED.value, MaterialType.DEED.value),
        (MaterialContentType.ONE_HOUSEHOLD_ONE_HOUSE.value, MaterialType.ONE_HOUSEHOLD_ONE_HOUSE.value),
        ((MaterialContentType.LAND_MAP.value, MaterialContentType.LAND_MAP_AREA.value), MaterialType.LAND_MAP.value),
        (MaterialContentType.ID_CARD.value, MaterialType.ID_CARD.value),
        (MaterialContentType.HOUSE_FLOOR_PLAN.value, MaterialType.HOUSE_FLOOR_PLAN.value),
        (MaterialContentType.HOUSEHOLD_REGISTER.value, MaterialType.HOUSEHOLD_REGISTER.value),
        (MaterialContentType.OWNERSHIP_SOURCE.value, MaterialType.OWNERSHIP_SOURCE.value)
    ])

    material_type = MaterialType.UNKNOWN.value

    for material_content, material_value in material_type_mapping.items():
        if isinstance(material_content, tuple):
            if all(content in ocr_text for content in material_content):
                material_type = material_value
                return material_type
        else:
            if material_content in ocr_text:
                material_type = material_value
                return material_type

    return material_type


def pre_process(task_id, images_path, preprocess_dir):
    if os.path.exists(preprocess_dir):
        shutil.rmtree(preprocess_dir)

    os.makedirs(preprocess_dir)

    res_dict = dict()
    file_list = os.listdir(images_path.split(".")[0])
    file_count = len(file_list)
    logger.info(f"Start Preprocessing ...")
    update_task_info(task_id, TaskInfoKey.LOG.value, f"Start Preprocessing ...")
    update_task_info(task_id, TaskInfoKey.TOTAL_FILE_COUNT.value, file_count)

    for idx, filename in enumerate(file_list):
        file_extension = filename.split(".")[-1]
        file_name = filename.split(".")[0]
        res_dict[filename] = {"file_type": file_extension.upper()}

        detection_type_list = ["pdf", "png", "jpg", "jpeg"]
        img_extension_list = ["png", "jpg", "jpeg"]
        if file_extension not in detection_type_list:
            continue

        logger.info(f"Preprocessing progress: {idx}/{file_count} ")
        update_task_info(task_id, TaskInfoKey.LOG.value, f"Preprocessing progress: {idx}/{file_count}")
        if file_extension in img_extension_list:
            shutil.copy(os.path.join(images_path, filename), os.path.join(preprocess_dir, f"{file_name}_page_0.png"))
        else:
            with pdfplumber.open(os.path.join(images_path, filename)) as pdf:
                ocr_text = ""
                for page_num, page in enumerate(pdf.pages):
                    default_text = page.extract_text()
                    ocr_text += default_text.replace(" ", "")

                    img = page.to_image()
                    tesseract_text = pytesseract.image_to_string(img.original, lang='chi_sim')
                    ocr_text += tesseract_text.replace(" ", "")
                    pdf_image = page.to_image().original

                    open_cv_image = cv2.cvtColor(np.array(pdf_image), cv2.COLOR_RGB2BGR)
                    cv2.imwrite(os.path.join(preprocess_dir, f"{file_name}_page_{page_num}.png"), open_cv_image)

                material_factory = MaterialFactory()
                material_type = material_factory.create_material_type(detect_material_type(ocr_text))

                if not res_dict[filename].get("material_type"):
                    res_dict[filename]["material_type"] = material_type
    print(res_dict)
    return res_dict


def generate_task_command(task_id, node, task_type):
    if task_type == TaskType.DETECT.value:

        res = generate_detect_task_command(task_id, node)

    elif task_type == TaskType.TRAINING.value:
        res = generate_training_task_command(task_id, node)

    else:
        raise ValueError("invalid parameters")

    return res





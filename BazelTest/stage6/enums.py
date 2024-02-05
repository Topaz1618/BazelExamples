"""
Author: Hang Yan
Date created: 2023/8/13
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

from enum import Enum


class MessageType(Enum):
    COMMAND = 1
    DATA = 2



class FileType(Enum):
    PDF = 0
    OTHERS = 1

class UserLevel(Enum):
    NORMAL = 0  # Represents a normal user
    ADMIN = 1   # Represents an admin user


class TaskType(Enum):
    DETECT = 1
    TRAINING = 2


class TaskErrorKeyword(Enum):
    ERROR = "Error"
    ERR = "Err"
    RAISE = "raise"
    ERROR_CASE_INSENSITIVE = "error"
    # TRACEBACK = "Traceback"


class TaskManagementType(Enum):
    START = 1
    STOP = 2


class ModelDescription(Enum):
    YOLO = "对象检测模型，识别图像中的多个对象，提供边框坐标信息"
    MaskRCNN = "像素分类模型，用于识别图像中的多个对象，提供像素级别掩码分割"
    RESNET = "图片分类模型，用于识别图片中主要物体类别"
    PADDLEOCR = "OCR模型，用于检测、识别图像中的文本"


class TrainModelType(Enum):
    YOLO = "YOLO"
    MaskRCNN = "Mask_RCNN"
    RESNET = "Resnet"
    PADDLEOCR = "PaddleOCR"


class TaskStatus(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4
    CANCELLED = 5
    RETRYING = 6
    TIMEOUT = 7
    TERMINATED = 8


class UploadStatus(Enum):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3


class TaskInfoKey(Enum):
    LOG = 'log'
    STATUS = 'status'
    NODE = 'node'
    RESULT = 'res'
    TASK_PID = 'task_pid'

    LAST_UPDATED_TIME = 'last_updated_time'
    WORK_CONN_STATUS = 'work_conn_status'

    TOTAL_FILE_COUNT = 'total_file_count'
    PROCESSED_FILE_COUNT = 'processed_file_count'

    EPOCH = 'epoch'
    ITERATIONS = 'iterations'
    CURRENT_EPOCH = 'current_epoch'
    CURRENT_ITERATION = 'current_iteration'


class WorkerStatus(Enum):
    IDLE = 1
    BUSY = 2
    OFFLINE = 3
    ERROR = 4
    RETRYING = 5


class WorkerConnectionStatus(Enum):
    CONNECTING = 1
    CONNECTED = 2
    FAILED = 3
    RETRYING = 4


class ModelSource(Enum):
    BUILT_IN = 1
    CUSTOM = 2

class DatasetSource(Enum):
    BUILT_IN = 1
    CUSTOM = 2


class TaskKeyType(Enum):
    LOG = "log"


if __name__ == "__main__":
    data = {
        "command_type": MessageType.COMMAND.value,
        "payload": "START"
    }
import os
import os

import pdfplumber
import pytesseract
import cv2
from time import time

import numpy as np

colors = np.random.randint(125, 255, (80, 3))

from enums import TaskStatus, TaskInfoKey
from task_utils import update_task_info, get_task_info, pre_process
from extensions import DetectionTaskManager


def handler(detect_floder, task_id, node):
    with pdfplumber.open(os.path.join(detect_floder)) as pdf:
        ocr_text = ""
        for page_num, page in enumerate(pdf.pages):
            default_text = page.extract_text()
            ocr_text += default_text.replace(" ", "")

            img = page.to_image()
            tesseract_text = pytesseract.image_to_string(img.original, lang='chi_sim')
            ocr_text += tesseract_text.replace(" ", "")

    res_dict = {
        "date": str(time()),
        "filename": detect_floder,
        "file_type": "PDF",
        "result": ocr_text,
    }

    update_task_info(task_id, TaskInfoKey.RESULT.value, res_dict)
    update_task_info(task_id, TaskInfoKey.LOG.value, f"Detection Task: [{task_id}] Already Completed!")
    update_task_info(task_id, TaskInfoKey.STATUS.value, TaskStatus.COMPLETED.value)

    task_obj = DetectionTaskManager()
    task_obj.update_task(task_id, TaskInfoKey.RESULT.value, res_dict)
    task_obj.update_task(task_id, "task_status", TaskStatus.COMPLETED.value)
    task_obj.close()

    return True


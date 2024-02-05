

def generate_model_gridfs_save_name(model_name, version, username):
    filename = f"{model_name}_{version}_{username}"
    return filename


def generate_dataset_gridfs_save_name(dataset_name, username):
    filename = f"{dataset_name}_{username}"
    return filename


def generate_detect_file_gridfs_save_name(detect, task_id):
    filename = f"{task_id}_{detect}"
    return filename

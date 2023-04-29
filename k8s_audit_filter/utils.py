import math
import os
import re
from typing import Union

from tqdm import tqdm  # type: ignore


def convert_bytes_size_to_mb(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_size_of_dir(path=""):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def create_dir(new_dir_path):
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)


def copy_files_to_folder(original_dir, target_dir, file_names):
    for file_name in tqdm(file_names):
        file = os.path.join(original_dir, file_name)
        os.system(f"cp {file} {target_dir}")


def get_file_names_in_folder(folder_name):
    if os.path.exists(folder_name):
        return os.listdir(folder_name)


def find_match(string, pattern=r"\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2}"):
    result = re.findall(pattern, string)
    if result:
        return result[0]


def filter_strings_by_time_interval(strings, start_time, end_time, pattern=r"\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2}"):
    if not start_time and not end_time or not bool(start_time) ^ bool(end_time):
        raise Exception("Start time or end time must be specified")
    if not start_time:
        start_time = "0000-00-00-00:00:00"
    if not end_time:
        end_time = "9999-99-99-99:99:99"
    if find_match(start_time, pattern) > find_match(end_time, pattern):
        raise Exception("Start time must be less than end time")
    if not find_match(start_time, pattern):
        raise Exception(f"Start time must be in format {pattern}")
    if not find_match(end_time, pattern):
        raise Exception(f"End time must be in format {pattern}")
    result = []
    for string in strings:
        if find_match(start_time, pattern) <= find_match(string, pattern) <= find_match(end_time, pattern):
            result.append(string)
    return result


def create_time_interval_dir(target_dir: str, start_time: str, end_time: str, new_dir_name: Union[str, None] = None):
    if not new_dir_name:
        new_dir_name = f"{start_time}_{end_time}"
    file_names = get_file_names_in_folder(target_dir)
    file_names_in_time_interval = filter_strings_by_time_interval(file_names, start_time, end_time)
    create_dir(new_dir_name)
    copy_files_to_folder(target_dir, new_dir_name, file_names_in_time_interval)
    return new_dir_name

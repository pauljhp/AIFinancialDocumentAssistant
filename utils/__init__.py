from .database import SQLDatabase
from typing import List, Any, Optional
from tempfile import TemporaryDirectory
import uuid
import json


def coalesce(*arg, return_val: Optional[Any]=None):
    """coalesce the inputs and return the first non-Null value
    If all null, return the `reeturn_val` value"""
    for val in arg:
        if val:
            return val
    if return_val:
        return return_val
    return None



def create_tempdir(session_id: str) -> TemporaryDirectory:
    return TemporaryDirectory(prefix=session_id)


def get_random_uuid():
    return uuid.uuid4()


def get_uuid_from_uname(username: str, fname: str):
    return uuid.uuid5(namespace=username, name=fname)


def save_result(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def load_result(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

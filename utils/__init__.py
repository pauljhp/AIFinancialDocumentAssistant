from .database import SQLDatabase
from typing import List, Any, Optional


def coalesce(*arg, return_val: Optional[Any]=None):
    """coalesce the inputs and return the first non-Null value
    If all null, return the `reeturn_val` value"""
    for val in arg:
        if val is not None:
            return val
    if return_val:
        return return_val
    return None
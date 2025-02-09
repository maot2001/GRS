from math import isnan
import os
from types import NoneType, FunctionType
from datetime import datetime
import pandas as pd

date_format = "%Y-%m-%d %H:%M:%S"

def dup(args: dict, id: str):
    tmp = args.copy()
    del tmp[id]
    return tmp

def clean(data, args, id=None, new_id=None):
    row = {}
    if id:
        if not isinstance(data[id], str) and isnan(data[id]): raise Exception
        
        if new_id: row[new_id] = str(data[id])
        else: row[id] = str(data[id])
    for arg in args:
        if arg in data:
            row[arg] = data[arg]
            if arg == 'time-id' and isinstance(row[arg], str):
                row[arg] = datetime.strptime(data[arg], date_format)
    return row

def binary_search_lte(arr, target):
    left, right = 0, len(arr) - 1
    result = -1  # To store the closest value found

    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid].id <= target:
            result = mid # Update result
            left = mid + 1  # Move to the right half
        else:
            right = mid - 1  # Move to the left half

    return result  # Return the closest value found or None

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    result = -1  # To store the closest value found

    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] <= target:
            result = mid # Update result
            left = mid + 1  # Move to the right half
        else:
            right = mid - 1  # Move to the left half

    return result  # Return the closest value found or None


def detect_type(key, atribs, files, url):
    types = {}

    for name_data in os.listdir(url):
        if not name_data.endswith('.csv'): continue
        
        this_atribs = files[name_data[:-4]]
        tmp = []

        if key in this_atribs:
            for a in this_atribs[key]:
                if a in atribs and not a in types:
                    tmp.append(a)

        if len(tmp) > 0:
            data = pd.read_csv(os.path.join(url, name_data))

            for _, row in data.iterrows():
                if len(tmp) == 0: break
                for a in tmp[::-1]:
                    if not type(row[a]) == NoneType:
                        types[a] = type(row[a])
                        tmp.remove(a)

    return types
            

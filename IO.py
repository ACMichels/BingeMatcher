import os
import pickle

def create_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def update_cache_structure():
    create_dir("Cache/")
    create_dir("Cache/Images/")

def cache_data(data: any, filename: str):
    update_cache_structure()
    path = f"Cache/{filename}.pkl"
    with open(path, 'wb') as file:
        pickle.dump(data, file)

def get_cache_exists(filename: str):
    update_cache_structure()
    path = f"Cache/{filename}.pkl"
    return os.path.isfile(path)

def get_cached_data(filename: str):
    update_cache_structure()
    path = f"Cache/{filename}.pkl"
    with open(path, 'rb') as file:
        return pickle.load(file)

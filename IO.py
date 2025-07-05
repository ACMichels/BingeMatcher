import os
import pickle


def cache_data(data, filename):
    path = f"Cache/{filename}.pkl"
    with open(path, 'wb') as file:
        pickle.dump(data, file)

def get_cache_exists(filename):
    path = f"Cache/{filename}.pkl"
    return os.path.isfile(path)

def get_cached_data(filename):
    path = f"Cache/{filename}.pkl"
    with open(path, 'rb') as file:
        return pickle.load(file)

import os
import requests
from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QPixmap, QImageReader

_threads = []
image_mem = {}

class ImageReader(QThread):
    image_loaded = Signal(QPixmap)

    def __init__(self, path):
        super().__init__()
        full_path = f"Cache/Images{path}"
        self.path = full_path

    def run(self):
        reader = QImageReader(self.path)
        pixmap = QPixmap.fromImage(reader.read())
        self.image_loaded.emit(pixmap)

class ImageLoader(QThread):
    image_loaded = Signal(QPixmap)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            url = f"https://image.tmdb.org/t/p/original{self.path}"
            response = requests.get(url)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.image_loaded.emit(pixmap)
        except Exception as e:
            print(f"Error loading image: {e}")

def get_cached_image(path):
    full_path = f"Cache/Images{path}"
    if os.path.isfile(full_path):
        reader = QImageReader(full_path)
        pixmap = QPixmap.fromImage(reader.read())
        return pixmap
    return None

def cache_image(path, pixmap):
    pixmap.save(f"Cache/Images{path}")

def check_cached(path):
    full_path = f"Cache/Images{path}"
    return os.path.isfile(full_path)

def store_image_in_memory(path, pixmap):
    image_mem[path] = pixmap

def load_image(path, resolve_function):

    if path in image_mem:
        resolve_function(image_mem[path])
        return

    worker = ImageReader(path) if check_cached(path) else ImageLoader(path)

    # Connect signals and slots
    worker.image_loaded.connect(resolve_function)
    worker.image_loaded.connect(lambda pm: store_image_in_memory(path, pm))
    worker.image_loaded.connect(lambda pm: cache_image(path, pm))
    def cleanup():
        _threads.remove(worker)
    worker.image_loaded.connect(cleanup)

    _threads.append(worker)

    worker.start()

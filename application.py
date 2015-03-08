import threading
import atexit
from flask import Flask

__author__ = 'Jonathan Horvath'

POOL_TIME = 5

shared_queue = []
data_lock = threading.Lock()
tracking_thread = threading.Thread()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    def interrupt():
        global tracking_thread
        tracking_thread.cancel()

    def process_queue():
        global shared_queue
        global tracking_thread
        global data_lock
        with data_lock:
            pass

        tracking_thread = threading.Timer(POOL_TIME, process_queue, ())
        tracking_thread.start()

    def start():
        global tracking_thread

        tracking_thread = threading.Timer(POOL_TIME, process_queue, ())
        tracking_thread.start()

    start()
    atexit.register(interrupt)
    return app


def add_to_queue(key):
    global shared_queue
    global data_lock
    with data_lock:
        shared_queue.append(key)

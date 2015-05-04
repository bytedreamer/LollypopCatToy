import threading
import atexit
from flask import Flask
from flask.ext.socketio import SocketIO
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import time

__author__ = 'Jonathan Horvath'

POLLING_TIME = 5
PLAY_TIME = 60

shared_queue = []
current_key = None
time_left = 0
data_lock = threading.Lock()
tracking_thread = threading.Thread()
socketio = SocketIO()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    global socketio
    socketio.init_app(app)

    def interrupt():
        global tracking_thread
        tracking_thread.cancel()

    def process_queue():
        global shared_queue
        global time_left
        global tracking_thread
        global data_lock
        global current_key
        with data_lock:
            if time_left <= 0 and len(shared_queue) >= 1:
                if current_key is not None:
                    socketio.emit(current_key, {'time_left': 0,
                                                'queue_length': 0,
                                                'is_ready': False}, namespace='/queue')

                current_key = shared_queue.pop()
                socketio.emit(current_key, {'time_left': PLAY_TIME,
                                            'queue_length': 0,
                                            'is_ready': True}, namespace='/queue')
                time_left = PLAY_TIME
            elif time_left > 0:
                time_left -= POLLING_TIME

            queue_length = 0
            for key in reversed(shared_queue):
                socketio.emit(key, {'time_left': (queue_length * PLAY_TIME) + time_left,
                                    'queue_length': queue_length + 1,
                                    'is_ready': False}, namespace='/queue')
                queue_length += 1

        tracking_thread = threading.Timer(POLLING_TIME, process_queue, ())
        tracking_thread.start()

    def start():
        global tracking_thread

        tracking_thread = threading.Timer(POLLING_TIME, process_queue, ())
        tracking_thread.start()

    start()
    atexit.register(interrupt)
    return app


def add_to_queue(key):
    global shared_queue
    global data_lock
    with data_lock:
        shared_queue.insert(0, key)


def activate_cat_toy(key, gpio_number):
    global current_key
    if key == current_key:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio_number, GPIO.OUT)
        GPIO.output(gpio_number, True)
        time.sleep(1)
        GPIO.output(gpio_number, False)
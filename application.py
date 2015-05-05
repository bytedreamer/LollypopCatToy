import threading
import atexit
from flask import Flask
from flask.ext.socketio import SocketIO
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges. "
          "You can achieve this by using 'sudo' to run your script")
import time

__author__ = 'Jonathan Horvath'

shared_queue = []
current_key = None
time_left = 0
data_lock = threading.Lock()
tracking_thread = threading.Thread()
socketio = SocketIO()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    play_time = app.config.get('PLAYING_TIME_IN_SECONDS')
    polling_time = app.config.get('POLLING_INTERVAL_IN_SECONDS')

    global socketio
    socketio.init_app(app)

    GPIO.setmode(GPIO.BCM)

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
                socketio.emit(current_key, {'time_left': play_time,
                                            'queue_length': 0,
                                            'is_ready': True}, namespace='/queue')
                time_left = play_time
            elif time_left > 0:
                time_left -= polling_time

            queue_length = 0
            for key in reversed(shared_queue):
                socketio.emit(key, {'time_left': (queue_length * play_time) + time_left,
                                    'queue_length': queue_length + 1,
                                    'is_ready': False}, namespace='/queue')
                queue_length += 1

        tracking_thread = threading.Timer(polling_time, process_queue, ())
        tracking_thread.start()

    def start():
        global tracking_thread

        tracking_thread = threading.Timer(polling_time, process_queue, ())
        tracking_thread.start()

    start()
    atexit.register(interrupt)
    return app


def add_to_queue(key):
    global shared_queue
    global data_lock
    with data_lock:
        shared_queue.insert(0, key)


def pulse_output(gpio_number):
    GPIO.setup(gpio_number, GPIO.OUT)
    GPIO.output(gpio_number, True)
    time.sleep(5)
    GPIO.output(gpio_number, False)


def activate_cat_toy(key, gpio_number):
    global current_key
    if key == current_key:
        pulsing_thread = threading.Thread(target=pulse_output, args=(gpio_number,))
        pulsing_thread.start()
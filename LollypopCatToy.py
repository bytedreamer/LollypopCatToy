from flask import render_template, make_response
from flask.ext.recaptcha import ReCaptcha
from uuid import uuid4, UUID
from application import create_app, add_to_queue, socketio, activate_cat_toy

__author__ = 'Jonathan Horvath'

app = create_app()
reCaptcha = ReCaptcha(app)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    if reCaptcha.verify():
        key = uuid4()
        add_to_queue(key)
        return render_template('register.html', key=key)
    else:
        return render_template('home.html')


@app.route('/play/<key>/<int:gpio_number>', methods=['POST'])
def play(key, gpio_number):
    activate_cat_toy(UUID(key), gpio_number)
    return make_response('', 204)


@socketio.on('connect', namespace='/queue')
def queue_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/queue')
def queue_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')

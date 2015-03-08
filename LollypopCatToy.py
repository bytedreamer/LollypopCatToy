from flask import render_template
from flask.ext.recaptcha import ReCaptcha
from uuid import uuid4
from application import create_app, add_to_queue

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


if __name__ == '__main__':
    app.run()

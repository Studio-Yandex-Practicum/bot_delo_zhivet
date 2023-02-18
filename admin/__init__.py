from flask import Flask, current_app, url_for, redirect

from admin.config import Config
from .database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        print(current_app.name)
    return app


app = create_app()


@app.route('/')
def index():
    return redirect(url_for('admin.index'))


from . import views  # noqa

if __name__ == '__main__':
    app.run(debug=True)

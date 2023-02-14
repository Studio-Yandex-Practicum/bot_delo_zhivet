from flask import Flask, current_app, render_template

from admin.config import Config

from .database import create_roles_and_superuser, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        print(current_app.name)
    return app


app = create_app()

create_roles_and_superuser()


@app.route("/")
def index():
    return render_template("index.html")


from . import views  # noqa

if __name__ == "__main__":
    app.run(debug=True)

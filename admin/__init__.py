import os

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, current_app, render_template
from sentry_sdk.integrations.flask import FlaskIntegration

from admin.config import Config

from .database import create_roles_and_superuser, db

load_dotenv(".env")

SENTRY_DSN_URL = os.getenv("SENTRY_DSN_URL", default="None")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        print(current_app.name)
    return app


sentry_sdk.init(
    dsn=SENTRY_DSN_URL,
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0,
)

app = create_app()

create_roles_and_superuser()


@app.route("/")
def index():
    return render_template("index.html")


from . import views  # noqa

if __name__ == "__main__":
    app.run(debug=True)

import os
import sys

from flask import Flask, current_app, redirect, url_for

from admin.config import Config

from .commands import admin_utils
from .database import db, get_not_existing_required_tables
from .messages import DB_NOT_READY_FOR_INIT_APP_ERROR, MISSING_REQUIRED_TABLES_ERROR

REQUIRED_TABLES = (
    "staff",
    "role",
)
try:
    not_existing_tables = get_not_existing_required_tables(REQUIRED_TABLES)
except Exception as error:
    sys.exit(DB_NOT_READY_FOR_INIT_APP_ERROR.format(app_name=__name__, details=str(error)))
if not_existing_tables:
    sys.exit(MISSING_REQUIRED_TABLES_ERROR.format(app_name=__name__, not_existing_tables=not_existing_tables))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.static_folder = os.path.join(app.root_path, "static")
    app.template_folder = os.path.join(app.root_path, "templates")
    app.static_url_path = None
    db.init_app(app)
    with app.app_context():
        print(current_app.name)
    return app


app = create_app()


@app.route("/")
def index():
    return redirect(url_for("admin.index"))


@app.route("/admin/static/<path:p>")
def static_redirect(p):
    return redirect("/static/" + p)


app.register_blueprint(admin_utils, cli_group=None)

from . import views  # noqa

if __name__ == "__main__":
    app.run(debug=True)

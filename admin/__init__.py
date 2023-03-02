import os
import sys

import sentry_sdk
from flask import Flask, current_app, redirect, render_template, url_for
from sentry_sdk.integrations.flask import FlaskIntegration

from .config import Config
from .database import create_roles_and_superuser, db, get_not_existing_required_tables
from .logger import get_logger
from .messages import DB_NOT_READY_FOR_INIT_APP_ERROR, MISSING_REQUIRED_TABLES_ERROR, START_LOGGING, STOP_LOGGING

logger = get_logger(__file__)
logger.info(START_LOGGING)
REQUIRED_TABLES = (
    "staff",
    "role",
)
try:
    not_existing_tables = get_not_existing_required_tables(REQUIRED_TABLES)
except Exception as error:
    logger.critical(DB_NOT_READY_FOR_INIT_APP_ERROR.format(app_name=__name__, details=str(error)))
    logger.info(STOP_LOGGING)
    sys.exit(DB_NOT_READY_FOR_INIT_APP_ERROR.format(app_name=__name__, details=str(error)))
if not_existing_tables:
    logger.critical(MISSING_REQUIRED_TABLES_ERROR.format(app_name=__name__, not_existing_tables=not_existing_tables))
    logger.info(STOP_LOGGING)
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


if Config.SENTRY_DSN_ADMIN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN_ADMIN,
        integrations=[
            FlaskIntegration(),
        ],
        traces_sample_rate=1.0,
        environment="admin",
    )

app = create_app()
create_roles_and_superuser()


@app.route("/")
def index():
    return redirect(url_for("admin.index"))


@app.route("/admin/static/<path:p>")
def static_redirect(p):
    return redirect("/static/" + p)


from . import views  # noqa


@app.errorhandler(404)
def page_not_found(e):
    return render_template("/admin/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

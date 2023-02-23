import os
import shutil

import click
import flask_admin
from flask import Blueprint, Flask, current_app, redirect, render_template

from admin.config import Config

from .database import create_roles_and_superuser, db


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
create_roles_and_superuser()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin/static/<path:p>")
def static_redirect(p):
    return redirect("/static/" + p)


bp = Blueprint("admin_utils", __name__)


@bp.cli.command("collectstatic")
@click.argument("static_folder", required=True)
@click.option("--overwrite/--no-overwrite", required=False, default=False)
def collectstatic(static_folder, overwrite):
    """
    CLI-команда для сбора статики на основе:
    https://github.com/flask-admin/flask-admin/issues/116#issuecomment-10190244
    Собирает статику Flask-Admin в папку, указанную в качестве параметра.

    Принимает два параметра:
    static_folder - обязательный параметр, имя папки для сбора статики.
    Папка создастся в корне приложения admin.
    overwrite - необязательный параметр. Отвечает за перезапись данных в
    папке для сбора статики.

    Примеры вызова:
    --------------------------------------------------------------------------------------
    flask collectstatic static
    >>>admin
    >>>Copying flask-admin static to: C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static
    --------------------------------------------------------------------------------------
    $ flask collectstatic static --overwrite
    >>>admin
    >>>Очищаем папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static'
    >>>Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static'
    """
    dst = os.path.join(app.root_path, static_folder)
    src = os.path.join(os.path.dirname(flask_admin.__file__), "static")
    try:
        if os.path.exists(dst) and overwrite:
            print(f"Очищаем папку '{dst}'")
            shutil.rmtree(dst)
        print(f"Собираем статику Flask-Admin в папку '{dst}'")
        shutil.copytree(src, dst)
        return True
    except Exception as error:
        print(f"В ходе сбора статики возникла ошибка. Подробности: {str(error)}")
        return False


app.register_blueprint(bp, cli_group=None)

from . import views  # noqa


@app.errorhandler(404)
def page_not_found(e):
    return render_template("/admin/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

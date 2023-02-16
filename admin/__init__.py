import os
import shutil

import click
import flask_admin
from flask import Blueprint, Flask, current_app, render_template

from admin.config import Config

from .database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.static_folder = "static123"
    app.template_folder = os.path.join(app.root_path, "templates")
    db.init_app(app)
    with app.app_context():
        print(current_app.name)
    return app


app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


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
    src = os.path.join(os.path.dirname(flask_admin.__file__), "static_BROKEN")
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

print(views.admin.index_view.endpoint)

if __name__ == "__main__":
    app.run(debug=True)

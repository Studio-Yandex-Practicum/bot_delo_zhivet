import os
import shutil

import click
import flask_admin
from flask import Blueprint

from .config import Config
from .messages import (
    COLLECT_STATIC_CLEAR_DIR_INFO,
    COLLECT_STATIC_ERROR,
    COLLECT_STATIC_INFO,
    COLLECT_TEMPLATES_ERROR,
    COLLECT_TEMPLATES_SUCCESS,
)


def recursive_copy_not_existing_items(src, dst):

    """Рекурсивное копирование несуществующих файлов и папок"""

    for item in os.listdir(src):
        if os.path.isdir(os.path.join(src, item)):
            dst_subdir = os.path.join(dst, item)
            if not os.path.exists(dst_subdir):
                os.mkdir(dst_subdir)
            src_subdir = os.path.join(src, item)
            recursive_copy_not_existing_items(src_subdir, dst_subdir)
        else:
            src_file = os.path.join(src, item)
            dst_file = os.path.join(dst, item)
            if not os.path.exists(dst_file):
                shutil.copy(src_file, dst_file)


admin_utils = Blueprint("admin_utils", __name__)


@admin_utils.cli.command("collectstatic")
@click.argument("static_folder", required=True)
@click.option("--overwrite/--no-overwrite", required=False, default=False)
def collectstatic(static_folder, overwrite):
    """
    CLI-команда для сбора статики на основе:

    \b
    https://github.com/flask-admin/flask-admin/issues/116#issuecomment-10190244

    \b
    Собирает статику Flask-Admin в папку, указанную в качестве параметра.

    Принимает два параметра:

    \b
    static_folder - обязательный параметр, имя папки для сбора статики.
    Папка создастся в корне приложения admin.

    \b
    overwrite - необязательный параметр. Отвечает за перезапись данных в
    папке для сбора статики.

    \b
    Примеры вызова:

    \b
    --------------------------------------------------------------------------------------
    $ flask collectstatic static
    >>>admin
    >>>Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static'

    \b
    --------------------------------------------------------------------------------------
    $ flask collectstatic static --overwrite
    >>>admin
    >>>Очищаем папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static'
    >>>Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static'
    """
    # для получения целевой директории лучше использовать app.root_path,
    # но это приведет к циклической зависимости
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), static_folder)
    src = os.path.join(os.path.dirname(flask_admin.__file__), "static")
    try:
        if os.path.exists(dst) and overwrite:
            print(COLLECT_STATIC_CLEAR_DIR_INFO.format(dst=dst))
            shutil.rmtree(dst)
        print(COLLECT_STATIC_INFO.format(dst=dst))
        shutil.copytree(src, dst)
        return True
    except Exception as error:
        print(COLLECT_STATIC_ERROR.format(details=str(error)))
        return False


@admin_utils.cli.command("collecttemplates")
@click.argument("templates_folder", required=True)
def collecttemplates(templates_folder):
    """
    CLI-команда для копирования HTML-шаблонов Flask-Admin
    в расположение, доступное для веб-сервера.
    Существующие шаблоны не перезаписываются.

    Принимает один параметр:

    \b
    templates_folder - обязательный параметр, имя папки для сохранения шаблонов.
    Папка создастся в корне приложения admin.

    \b
    --------------------------------------------------------------------------------------
    $ flask collecttemplates templates

    \b
    >>>Копирование шаблонов Flask-Admin завершено успешно
    """
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), templates_folder)
    src_common = os.path.join(os.path.dirname(flask_admin.__file__), "templates")
    src = os.path.join(src_common, Config.BOOTSTRAP_VERSION)
    try:
        if not os.path.exists(dst):
            os.mkdir(dst)
        recursive_copy_not_existing_items(src, dst)
        print(COLLECT_TEMPLATES_SUCCESS)
        return True
    except Exception as error:
        print(COLLECT_TEMPLATES_ERROR.format(details=str(error)))
        return False

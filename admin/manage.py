import argparse
import logging
import os
import shutil
import sys

import flask_admin
from config import Config
from messages import (
    APP_TEMPLATE_FOLDER_COPY_SUCCESS,
    APP_TEMPLATE_FOLDER_NOT_FOUND,
    COLLECT_STATIC_CLEAR_DIR_INFO,
    COLLECT_STATIC_ERROR,
    COLLECT_STATIC_INFO,
    COLLECT_TEMPLATES_ERROR,
    COLLECT_TEMPLATES_SUCCESS,
    COMMON_ERROR,
    START_LOGGING,
    STOP_LOGGING,
    UNKNOWN_COMMAND,
)

logging.root.setLevel(logging.NOTSET)

# Переопределение логгера для manage.py
# При попытке импорта по цепочке manage.py не импортирует модули через '.'
# из-за ошибки attempted relative import with no known parent package
# Изящнее решения не нашел


def get_logger(file, display=False):

    """Создание и настройка логгера."""

    log_path = os.path.join(os.path.dirname(file), Config.LOG_REL_PATH)
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file = os.path.join(log_path, os.path.basename(file) + Config.LOG_EXTENSION)
    logger = logging.getLogger(os.path.basename(file))
    formatter = logging.Formatter(Config.LOG_FORMAT)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(Config.LOG_DEFAULT_LVL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if display:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(Config.LOG_DEFAULT_LVL)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


logger = get_logger(__file__, display=True)
logger.info(START_LOGGING)


def recursive_copy_not_existing_items(src, dst):

    """Рекурсивное копирование несуществующих файлов и папок"""
    logger.debug("start recurse")
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


class Manage(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="Запуск утилит командной строки из Manage.py",
            usage="""
            python manage.py <command> [<args>]
            Утилита командной строки для запуска команд перед развертыванием
            приложения.
            Возможные команды:
            - collectstatic - сборка статических файлов Flask-Admin;
            - collecttemplates - сборка шаблонов Flask-Admin;
            """,
        )
        parser.add_argument("command", help="Запуск команд")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(UNKNOWN_COMMAND.format(command=args.command))
            logger.warning(UNKNOWN_COMMAND.format(command=args.command))
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def collectstatic(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="""
                Функция сбора статики, независимая от инициализации приложения Flask.
                Производит копирование статического содержимого модуля Flask-Admin в
                папку статического содержимого самого приложения.
                --------------------------------------------------------------------------------------
                Общая информация о вызове:
                python manage.py collectstatic <required: folder> <optional: overwrite>
                folder - относительный путь к папке статики;
                overwrite - флаг перезаписи существующей папки статики.
                --------------------------------------------------------------------------------------
                Примеры вызовов и возвратов:
                --------------------------------------------------------------------------------------
                $ python manage.py collectstatic --static_folder static_demo
                >>> Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static_demo'
                --------------------------------------------------------------------------------------
                $ python manage.py collectstatic --static_folder static_demo
                >>> Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static_demo'
                >>> В ходе сбора статики возникла ошибка. Подробности:
                >>> [WinError 183] Невозможно создать файл, так как он уже существует:
                    'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static_demo'
                --------------------------------------------------------------------------------------
                $ python manage.py collectstatic --static_folder static_demo --overwrite
                >>> Очищаем папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static_demo'
                >>> Собираем статику Flask-Admin в папку 'C:\\Dev\\delo_zhivet\\bot_delo_zhivet\\admin\\static_demo'
                --------------------------------------------------------------------------------------
            """,
        )
        parser.add_argument("--static_folder", required=True, help="Папка для сохранения статики")
        parser.add_argument(
            "--overwrite",
            action="store_true",
            required=False,
            help="Параметр для перезаписи папки статики в случае её существования",
        )
        args = parser.parse_args(sys.argv[2:])
        static_folder = args.static_folder
        overwrite = args.overwrite
        dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), static_folder)
        src = os.path.join(os.path.dirname(flask_admin.__file__), "static")
        try:
            if os.path.exists(dst) and overwrite:
                print(COLLECT_STATIC_CLEAR_DIR_INFO.format(dst=dst))
                logger.info(COLLECT_STATIC_CLEAR_DIR_INFO.format(dst=dst))
                shutil.rmtree(dst)
            print(COLLECT_STATIC_INFO.format(dst=dst))
            logger.info(COLLECT_STATIC_INFO.format(dst=dst))
            shutil.copytree(src, dst)
            return True
        except Exception as error:
            print(COLLECT_STATIC_ERROR.format(details=str(error)))
            logger.error(COLLECT_STATIC_ERROR.format(details=str(error)))
            return False

    def collecttemplates(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="""
                Функция сбора шаблонов, независимая от инициализации приложения Flask.
                Производит копирование шаблонов модуля Flask-Admin в папку шаблонов самого приложения.
                Функция не перезаписывает имеющиеся в целевой папке шаблоны.
                --------------------------------------------------------------------------------------
                Общая информация о вызове:
                $ python manage.py collecttemplates templates_demo <required: path> <optional: --merge>
                path - относительный путь к папке статики;
                merge - режим слияния шаблонов из папки шаблонов проекта и шаблонов Flask-Admin.
                При режиме merge сначал будут скопированы имеющиеся шаблоны приложены, потом шаблоны
                Flask-Admin без перезаписи.
                --------------------------------------------------------------------------------------
                Примеры вызовов и возвратов:
                --------------------------------------------------------------------------------------
                $ python manage.py collecttemplates --templates_folder templates_demo
                >>> Копирование шаблонов Flask-Admin завершено успешно
                --------------------------------------------------------------------------------------
                $ python manage.py collecttemplates --templates_folder templates_demo --merge
                >>> Копирование существующих шаблонов успешно завершено
                >>> Копирование шаблонов Flask-Admin завершено успешно
                --------------------------------------------------------------------------------------
                Если запуск производится уровнем выше папки приложения, необходимо указать папку
                приложения в пути до manage.py и папки статики:
                --------------------------------------------------------------------------------------
            """,
        )
        parser.add_argument("--templates_folder", required=True, help="Папка для сохранения шаблонов")
        parser.add_argument(
            "--merge",
            action="store_true",
            required=False,
            help=(
                "Слияние текущих шаблонов приложения и шаблонов Flask_admin. "
                "Если параметр не указан, будут скопированы только шаблоны Flask-Admin"
                "Если шаблон приложения после копирвоания находится по тому же пути, "
                "что и шаблон Flask-Admin, сохраняется шаблон приложения"
            ),
        )
        args = parser.parse_args(sys.argv[2:])
        templates_folder = args.templates_folder
        merge = args.merge
        dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), templates_folder)
        src_common = os.path.join(os.path.dirname(flask_admin.__file__), "templates")
        src = os.path.join(src_common, Config.BOOTSTRAP_VERSION)
        try:
            if not os.path.exists(dst):
                os.mkdir(dst)
            if merge:
                existing_templates_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
                if not os.path.exists(existing_templates_folder):
                    print(APP_TEMPLATE_FOLDER_NOT_FOUND)
                    logger.warning(APP_TEMPLATE_FOLDER_NOT_FOUND)
                else:
                    recursive_copy_not_existing_items(existing_templates_folder, dst)
                    print(APP_TEMPLATE_FOLDER_COPY_SUCCESS)
                    logger.info(APP_TEMPLATE_FOLDER_COPY_SUCCESS)
            recursive_copy_not_existing_items(src, dst)
            print(COLLECT_TEMPLATES_SUCCESS)
            logger.info(COLLECT_TEMPLATES_SUCCESS)
            return True
        except Exception as error:
            print(COLLECT_TEMPLATES_ERROR.format(details=str(error)))
            logger.warning(COLLECT_TEMPLATES_ERROR.format(details=str(error)))
            return False


if __name__ == "__main__":
    try:
        Manage()
        logger.info(STOP_LOGGING)
        sys.exit(0)
    except Exception as error:
        logger.error(COMMON_ERROR.format(details=str(error)))
        sys.exit(1)

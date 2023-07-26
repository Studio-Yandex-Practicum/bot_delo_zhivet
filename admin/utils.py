from time import time

import jwt
from Levenshtein import distance
from sqlalchemy.orm.attributes import InstrumentedAttribute
from structlog import get_logger
from wtforms.validators import ValidationError

from admin.config import settings
from admin.locales import FIELD_TRANSLATION_RU
from admin.messages import TOKEN_VALIDATION_ERROR
from src.core.db.model import Staff

logger = get_logger("admin_logger")


def get_readonly_dict(fields):
    """
    Возвращает словарь для установки полей, перечисленных
    в параметре, в значение readonly для дальнейшей передачи
    в свойство form_widget_args вью-класса
    """
    readonly_fileds = dict()
    for field in fields:
        readonly_fileds[field] = {"readonly": True}
    return readonly_fileds


def get_translated_lables(fields):
    """Функция для перевода полей на русский язык"""
    labels = dict()
    for field in fields:
        labels[field] = FIELD_TRANSLATION_RU.get(field, field)
    return labels


def get_table_fields_from_model(model):
    """
    Функция для извлечения списка полей, отображаемых в админке,
    из модели
    """
    fields = []
    for field, value in dict(model.__dict__).items():
        if isinstance(value, InstrumentedAttribute):
            fields.append(field)
    return fields


def get_sortable_fields_list(all_columns: list, name_relation: dict[str:str]) -> list:
    """
    Функция для создания списка сортируемых полей и замены field_name на (field_name, <relation name>.<column name>)
    для relationship
    В словаре указываются 'field_name': 'relation_name.column_name'.
    """
    fields = []
    for field_name in all_columns:
        if field_name in name_relation.keys():
            fields.append((field_name, name_relation[field_name]))
        else:
            fields.append(field_name)
    return fields


def get_reset_password_token(user, expires_in=int(settings.PASSWORD_RESET_TOKEN_TTL)):
    return jwt.encode(
        {"reset_password": user.login, "exp": time() + expires_in},
        settings.SECRET_KEY,
        algorithm=settings.PASSWORD_RESET_TOKEN_ALGORITHM,
    )


def verify_reset_password_token(token):
    try:
        login = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=settings.PASSWORD_RESET_TOKEN_ALGORITHM,
        )["reset_password"]
    except Exception as e:
        logger.warning(TOKEN_VALIDATION_ERROR, token=token, details=str(e))
        return
    return Staff.query.filter_by(login=login).first()


def check_tag_uniqueness(model, existing_tags):
    """Функция для проверки уникальности тега."""
    if any(distance(tag.name.lower(), model.name.lower()) < 5 for tag in existing_tags):
        raise ValidationError("В базе уже существует похожий тег!")

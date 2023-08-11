from sqlalchemy.orm.attributes import InstrumentedAttribute
from .locales import FIELD_TRANSLATION_RU


def get_table_fields_from_model(model):
    """
    Извлечения списка полей из модели, для отображения в админке.
    """
    fields = []

    model_dict = dict(model.__dict__)

    for field, value in model_dict.items():
        if isinstance(value, InstrumentedAttribute):
            fields.append(field)

    return fields


def get_translated_labels(columns):
    """ Вернет labels на русском языке. """

    labels = dict()

    for column in columns:
        labels[column] = FIELD_TRANSLATION_RU.get(column, column)

    return labels

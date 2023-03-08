import re


def phone_number_validate(user_input):
    validate_phone_number_pattern = "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"  # noqa
    return re.match(validate_phone_number_pattern, user_input)


def format_numbers(phone_number: str) -> str:
    numbers = list(filter(str.isdigit, phone_number))[1:]
    return "+7{}{}{}{}{}{}{}{}{}{}".format(*numbers)

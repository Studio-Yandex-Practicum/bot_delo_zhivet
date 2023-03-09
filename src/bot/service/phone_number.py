import re


def phone_number_validate(user_input):
    validate_phone_number_pattern = (
        "^\+?(?!(?:.*-){3})(?!.*--)(?=[^()]*\([^()]+\)[^()]*$|[^()]*$)(?!.*-.*[()])(?:[()-]*\d){11}[()-]*$"  # noqa
    )
    return re.match(validate_phone_number_pattern, user_input)

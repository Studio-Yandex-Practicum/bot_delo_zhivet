def phone_number_validate(user_input):
    numbers = list(filter(str.isdigit, user_input))[1:]
    if len(numbers) == 10:
        return "+7{}{}{}{}{}{}{}{}{}{}".format(*numbers)
    return None


def format_numbers(phone_number: str) -> str:
    numbers = list(filter(str.isdigit, phone_number))[1:]
    return "+7({}{}{}){}{}{}-{}{}-{}{}".format(*numbers)

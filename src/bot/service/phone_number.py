def phone_number_validate(user_input):
    numbers = list(filter(str.isdigit, user_input))
    if len(numbers) == 11 and (numbers[0] == "7" or numbers[0] == "8"):
        return "+7{}{}{}{}{}{}{}{}{}{}".format(*numbers[1:])
    return None


def format_numbers(phone_number: str) -> str:
    numbers = list(filter(str.isdigit, phone_number))[1:]
    return "+7({}{}{}){}{}{}-{}{}-{}{}".format(*numbers)

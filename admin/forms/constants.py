MIN_LENGTH_LOGIN = 4
MAX_LENGTH_LOGIN = 10
MIN_LENGTH_PASSWORD = 8
MAX_LENGTH_PASSWORD = 255

LABEL_FIELDS = {
    'login': 'Введите логин',
    'password': 'Введите пароль',
    'password_repeat': 'Повторите пароль',
    'email': 'Электронная почта'
}

ERROR_MESSAGE = {
    'wrong_user': 'Пользователь с таким логином: {} не существует',
    'required_field': 'Это поле является обязательным',
    'min_length_login': f'Минимальная длинна логина {MIN_LENGTH_LOGIN} символов',
    'min_length_password': f'Минимальная длинна пароля {MIN_LENGTH_PASSWORD} символов',
    'incorrect_password': 'Неверный пароль <p>Забыли пароль? <a href="{}">Нажмите здесь, чтобы восстановить его</a></p>',
    'incorrect_email': 'Введите правильный адрес электронной почты',
    'login_busy': 'Пользователь с такой учетной записью уже существует',
    'email_busy': 'Пользователь с таким адресом электронной почты существует',
    'email_not_found': 'Пользователь с таким адресом электронной почты не найден',
    'equal_passwords': "Пароли не совпадают",
    'should_not_match': 'Логин и пароль не должны совпадать'
}

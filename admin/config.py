# # Create dummy secrey key so we can use sessions
# SECRET_KEY = '123456790'
#
# # Create in-memory database
# DATABASE_FILE = 'sample_db.sqlite'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
# SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

# URLs
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Включает регистрацию
SECURITY_REGISTERABLE = True
SECURITY_REGISTER_URL = "/register/"
SECURITY_SEND_REGISTER_EMAIL = False

# Включет сброс пароля
SECURITY_RECOVERABLE = True
SECURITY_RESET_URL = "/reset/"
SECURITY_SEND_PASSWORD_RESET_EMAIL = True

# Включает изменение пароля
SECURITY_CHANGEABLE = True
SECURITY_CHANGE_URL = "/change/"
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

import os
from time import time

import jwt
from werkzeug.security import check_password_hash, generate_password_hash


class ExtraUserMixin:
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.login

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.login, "exp": time() + expires_in},
            os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY"),
            algorithm="HS256",
        )

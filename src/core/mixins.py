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

    def get_reset_token(self, expires=500):
        return jwt.encode(
            {
                "reset_password": self.username,
                "exp": time() + expires,
            },
            key=os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY"),
        )

    def verify_reset_token(self, token):
        try:
            username = jwt.decode(token, key=os.getenv("ADMIN_SECRET_KEY", default="SECRET_KEY"))["reset_password"]
            print(username)
        except Exception as e:
            print(e)
            return
        return

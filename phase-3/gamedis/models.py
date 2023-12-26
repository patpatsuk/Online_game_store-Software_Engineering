# Database schema
import datetime
import time

from flask_login import UserMixin, current_user, AnonymousUserMixin

from . import db


class User(db.Model, UserMixin, AnonymousUserMixin):
    """ Database table: user
        each user account setting/properties defined here.

        #Attribute:
            uname -> username,
            alias -> alias (not null),
            password -> password,
        """
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    uname = db.Column(db.String(26), unique=True)  # username
    alias = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String())

    def __str__(self):
        return self.alias

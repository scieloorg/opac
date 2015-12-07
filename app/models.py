# coding: utf-8
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from . import dbsql as db
from . import login_manager
import notifications


# Create user model.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    _password = db.Column(db.String(128))
    email_confirmed = db.Column(db.Boolean, default=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        """
        compares a string with the hashed password stored for that user.
        """
        return check_password_hash(self._password, plaintext)

    def send_confirmation_email(self):
        return notifications.send_confirmation_email(self.email)

    def send_reset_password_email(self):
        return notifications.send_reset_password_email(self.email)

    # Required for administrative interface
    def __unicode__(self):
        return self.email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    db.drop_all()
    db.create_all()
    # passwords are hashed, to use plaintext passwords instead:
    test_user = User(email="test@test.com", password="test")
    db.session.add(test_user)

    db.session.commit()
    return

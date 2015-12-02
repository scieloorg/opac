# coding: utf-8
from . import dbsql as db
from . import login_manager
from werkzeug.security import generate_password_hash


# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))

    # # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

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
    test_user = User(email="test@test.com", password=generate_password_hash("test"))
    db.session.add(test_user)

    db.session.commit()
    return

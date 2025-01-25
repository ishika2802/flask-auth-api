from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = str(user_id)  # Flask-Login requires a string ID
        self.username = username
        self.email = email

    def get_id(self):
        # This is a required method for Flask-Login
        return self.id

    def __repr__(self):
        return f"<User {self.username}>"

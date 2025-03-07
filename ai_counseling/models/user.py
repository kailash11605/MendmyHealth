from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        # Note: We don't store the password in the User object for security reasons


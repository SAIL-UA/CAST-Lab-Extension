# custom_authenticator.py

from jupyterhub.auth import Authenticator

class CustomAuthenticator(Authenticator):
    def authenticate(self, handler, data):
        # Implement your custom authentication logic here
        username = data['username']
        password = data['password']

        # Dummy user accounts for testing purposes
        dummy_users = {
	    "saillab":"saillab",
            "Jiaqi": "123456",
            "user1": "password1",
            "user2": "password2",
        }

        if username in dummy_users and dummy_users[username] == password:
            return username
        else:
            return None

    def get_users(self):
        # Implement a method to return a list of authorized users
        return ["user1", "user2"]


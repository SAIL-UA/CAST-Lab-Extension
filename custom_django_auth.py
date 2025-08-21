from jupyterhub.auth import Authenticator
from traitlets import Unicode
import requests

class DjangoAuthenticator(Authenticator):
    api_url = Unicode("http://backend:8051", config=True)
    enable_auth_state = True

    async def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        try:
            res = requests.post(
                f"{self.api_url}/users/login/",
                json={"username": username, "password": password},
                timeout=5
            )
            res.raise_for_status()
            body = res.json()

            access_token = body.get('access')
            refresh_token = body.get('refresh')
            if access_token:
                return {
                    "name": username,
                    "auth_state": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": body.get("user", {})
                    }
                }
        except Exception as e:
            self.log.error(f"Error contacting Django API: {e}")

        return None
    
    async def pre_spawn_start(self, user, spawner):
        """Optional: Make access_token and refresh_token available to the user server"""
        auth_state = await user.get_auth_state()
        if not auth_state:
            return
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['REFRESH_TOKEN'] = auth_state['refresh_token']
        spawner.environment['STORYSTUDIO_API_URL'] = f"{self.api_url}/api/"

import sys
import os
sys.path.append(os.path.dirname(__file__))
from dockerspawner import DockerSpawner
from jupyterhub.app import JupyterHub

c = get_config()  # noqa

# ---------------------------
# Authentication
# ---------------------------
c.JupyterHub.authenticator_class = "custom_django_auth.DjangoAuthenticator"
c.DjangoAuthenticator.api_url = 'http://backend:8051'
c.Authenticator.admin_users = {"aii03admin"}
c.Authenticator.allow_all = True


# ---------------------------
# Spawner Config
# ---------------------------
c.JupyterHub.spawner_class = DockerSpawner
c.DockerSpawner.image = 'cast-notebook'
c.DockerSpawner.remove_containers = True

c.DockerSpawner.volumes = {
    '/data/CAST_ext/users/{username}/workspace': '/home/jovyan/work',
}

c.DockerSpawner.network_name = 'cast-network'
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.extra_host_config = {"network_mode": "cast-network"}

c.Spawner.default_url = "/lab"
c.Spawner.debug = True
c.Spawner.http_timeout = 60

# ---------------------------
# Hub Networking
# ---------------------------
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8080'
c.JupyterHub.bind_url = 'http://0.0.0.0:8000'
c.JupyterHub.base_url = '/jupyterhub/'
c.JupyterHub.allow_named_servers = True
c.JupyterHub.default_url = "/jupyterhub/hub/home"


# ---------------------------
# Proxy / Tornado
# ---------------------------
c.JupyterHub.tornado_settings = {
    "no_cache_static": True,
    "slow_spawn_timeout": 0,
    "xsrf_cookies": True,
    "cookie_path": "/jupyterhub/"
}

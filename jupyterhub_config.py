import sys
import os
sys.path.append(os.path.dirname(__file__))
from dockerspawner import DockerSpawner
from jupyterhub.app import JupyterHub
import subprocess

c = get_config()  # noqa

# ---------------------------
# Authentication
# ---------------------------
c.JupyterHub.authenticator_class = "custom_django_auth.DjangoAuthenticator"
c.DjangoAuthenticator.api_url = 'http://backend:8051'
c.Authenticator.admin_users = {"egjackson"}
c.Authenticator.allow_all = True


# ---------------------------
# Spawner Config
# ---------------------------
c.JupyterHub.spawner_class = DockerSpawner
c.DockerSpawner.image = 'cast-notebook'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.notebook_dir = "/home/jovyan/work"

# c.DockerSpawner.volumes = {
#     '/data/CAST_ext/users/{username}/workspace': '/home/jovyan/work',
# }
c.DockerSpawner.extra_create_kwargs = {"user": "1000:100"} 

c.DockerSpawner.network_name = 'cast-network'
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.extra_host_config = {"network_mode": "cast-network"}

c.DockerSpawner.environment = {
    "NB_UID": "1000",
    "NB_GID": "100",
    "GRANT_SUDO": "yes",
    "CHOWN_EXTRA": "/home/jovyan/work",
    "CHOWN_EXTRA_OPTS": "-R",
}

def ensure_host_workspace(spawner):
    username = spawner.user.name
    host_dir = f"/data/CAST_ext/users/{username}/workspace"

    # 1) Make sure the directory exists
    os.makedirs(host_dir, exist_ok=True)

    # 2) Best-effort owner/perms (Hub must run with rights to chown/chmod this path)
    try:
        os.chown(host_dir, 1000, 100)              # jovyan:users
    except PermissionError:
        spawner.log.warning(f"Cannot chown {host_dir}; check Hub privileges")

    # group rwX + setgid (children inherit 'users' group)
    subprocess.run(["chmod", "2775", host_dir], check=False)
    subprocess.run(["chmod", "-R", "g+rwX", host_dir], check=False)

    # 3) SELinux relabel so containers can write (no-op if SELinux not enabled)
    subprocess.run(["chcon", "-Rt", "svirt_sandbox_file_t", host_dir], check=False)

    # 4) Bind mount with :Z (SELinux relabel) and rw
    binds = {
        host_dir: {
            "bind": "/home/jovyan/work",
            "mode": "rw,Z",
        }
    }
    ehc = dict(getattr(spawner, "extra_host_config", {}) or {})
    ehc["binds"] = binds
    spawner.extra_host_config = ehc

c.Spawner.pre_spawn_hook = ensure_host_workspace


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
c.JupyterHub.trust_xheaders = True


c.ServerApp.trust_xheaders = True

# ---------------------------
# Proxy / Tornado
# ---------------------------
c.JupyterHub.tornado_settings = {
    "no_cache_static": True,
    "slow_spawn_timeout": 0,
    "xsrf_cookies": True,
    "cookie_path": "/jupyterhub/"
}



"""
nbgitpuller link:
https://cast-storystudio.com/jupyterhub/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Flujiec2020%2FUMBC-IS296-SP24&targetPath=UMBC%2F&urlpath=lab%2Ftree%2FUMBC%2Fhw%2Fhw01%2Fhw01.ipynb%3Fautodecode
"""
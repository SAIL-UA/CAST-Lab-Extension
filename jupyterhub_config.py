from custom_sudospawner import SudoSpawner

c = get_config()  # noqa

c.JupyterHub.authenticator_class = "pam"
c.LocalAuthenticator.create_system_users = False

# Optionally set a global password that all users must use
# c.DummyAuthenticator.password = "your_password"

c.JupyterHub.spawner_class = SudoSpawner

# c.JupyterHub.ssl_key = './certs/jupyterhub.cs.ua.edu.key'
# c.JupyterHub.ssl_cert = './certs/jupyterhub_cs_ua_edu_cert.cer'
# c.JupyterHub.bind_url = 'https://jupyterhub.cs.ua.edu:443'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8080'


# only listen on localhost for testing
#c.JupyterHub.bind_url = 'http://127.0.0.1:8080'

# don't cache static files
c.JupyterHub.tornado_settings = {
    "no_cache_static": True,
    "slow_spawn_timeout": 0,
    "xsrf_cookies": False
}

# c.Spawner.notebook_dir='/home/saillab/CAST/CAST_ext/users/{username}/workspace'
# c.Spawner.args = ['--NotebookApp.terminals_enabled=False', '--allow-root']

c.JupyterHub.allow_named_servers = True
c.JupyterHub.default_url = "/hub/home"

c.Authenticator.allowed_users = {
  "emily",
  "user1",
  "user2",
  "user3",
  "user4",
  "user5",
  "user6",
  "user7",
  "user8",
  "user9",
  "user10",
  "user11",
  "user12",
  "user13",
  "user14",
  "user15",
  "user16",
  "user17",
  "user18",
  "user19",
  "user20",
  "user21",
  "user22",
  "user23",
  "user24",
  "user25",
  "user26",
  "user27",
  "user28",
  "user29",
  "user30",
  "sli90"
  }
c.Authenticator.delete_invalid_users = True

# c.ServerApp.terminals_enabled = False

# make sure admin UI is available and any user can login
c.Authenticator.admin_users = {"aii03admin"}
# c.Authenticator.allow_all = True

"""sample jupyterhub config file for testing

configures jupyterhub with dummyauthenticator and simplespawner
to enable testing without administrative privileges.
"""

c = get_config()  # noqa

c.JupyterHub.authenticator_class = "dummy"

# Optionally set a global password that all users must use
# c.DummyAuthenticator.password = "your_password"

c.JupyterHub.spawner_class = "simple"

c.JupyterHub.ssl_key = './jupyterhub.cs.ua.edu.key'
c.JupyterHub.ssl_cert = './jupyterhub_cs_ua_edu_cert.cert'
#c.JupyterHub.hub_bind_url = '127.0.0.1:8080'
c.JupyterHub.bind_url = 'https://20.98.128.247:443'

# only listen on localhost for testing
#c.JupyterHub.bind_url = 'http://127.0.0.1:8080'

# don't cache static files
c.JupyterHub.tornado_settings = {
    "no_cache_static": True,
    "slow_spawn_timeout": 0,
}

c.Spawner.notebook_dir="~/Public/"
c.Spawner.args = ['--NotebookApp.terminado_settings={"shell_command":["false"]}']

c.JupyterHub.allow_named_servers = True
c.JupyterHub.default_url = "/hub/home"

# make sure admin UI is available and any user can login
c.Authenticator.admin_users = {"admin"}
c.Authenticator.allow_all = True

import os
import datetime
from jupyterhub.spawner import LocalProcessSpawner

class SudoSpawner(LocalProcessSpawner):
  async def start(self):
    jupyter_base_dir = '/home/aii03admin/miniconda3/envs/CAST'
    self.env.update({'JUPYTER_CONFIG_DIR': os.path.join(jupyter_base_dir, "etc/jupyter"),
                     'JUPYTER_DATA_DIR': os.path.join(jupyter_base_dir, "share/jupyter"),
                     'JUPYTER_RUNTIME_DIR': '/home/aii03admin/.local/share/jupyter/runtime',
                     'JUPYTER_SERVERAPP_TERMINALS_ENABLED': 'false'})
    user = self.user.name
    stamp = datetime.datetime.now()
    base = f"/home/aii03admin/CAST_ext/users/{user}"
    wd = os.path.join(base, "workspace")
    cache = os.path.join(wd, "cache")

    self.env.update({'CACHE_PATH': cache})

    os.makedirs(wd, exist_ok=True)
    os.chmod(wd, 0o777)
    os.makedirs(cache, exist_ok=True)
    os.chmod(cache, 0o777)

    self.notebook_dir = wd
    # self.args = ['--NotebookApp.terminals_enabled=False', '--allow-root']
    self.args = ['--allow-root']

    log_path = os.path.join("/home/aii03admin/CAST_ext/logs",user)
    os.makedirs(log_path, mode=0o777, exist_ok=True)
    log_file = f"/home/aii03admin/CAST_ext/logs/{user}/{stamp}.json"

    open(log_file, "w")
    os.chmod(log_file, 0o777)

    
    self.env.update({'LOG_FILE': log_file})
    return await super().start()
    
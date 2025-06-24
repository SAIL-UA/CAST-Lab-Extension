import os
import grp
import pwd
import datetime
from sqlite3.dbapi2 import Time
from jupyterhub.spawner import LocalProcessSpawner
import json

class SudoSpawner(LocalProcessSpawner):
  async def start(self):
    jupyter_base_dir = '/data/.conda/envs/cast'
    self.env.update({'JUPYTER_CONFIG_DIR': os.path.join(jupyter_base_dir, "etc/jupyter"),
                     'JUPYTER_DATA_DIR': os.path.join(jupyter_base_dir, "share/jupyter"),
                     'JUPYTER_RUNTIME_DIR': '/home/aii03admin/.local/share/jupyter/runtime',
                     'JUPYTER_SERVERAPP_TERMINALS_ENABLED': 'false'})
    user = self.user.name
    timestamp = datetime.datetime.now()
    base = f"/data/CAST_ext/users/{user}"
    wd = os.path.join(base, "workspace")
    cache = os.path.join(wd, "cache")

    self.env.update({'CACHE_PATH': cache})

    uid = pwd.getpwnam('root').pw_uid
    gid = grp.getgrnam('jupyter_users').gr_gid

    os.makedirs(wd, exist_ok=True)
    os.chown(wd,uid,gid)
    os.chmod(wd, 0o2770)
    os.makedirs(cache, exist_ok=True)
    os.chown(cache,uid,gid)
    os.chmod(cache, 0o2770)

    self.notebook_dir = wd
    
    # self.args = ['--NotebookApp.terminals_enabled=False', '--allow-root']
    self.args = ['--allow-root']
    self.cpu_limit=1
    self.mem_limit=3
    

    log_path = os.path.join("/data/CAST_ext/logs",user)
    os.makedirs(log_path, mode=0o777, exist_ok=True)
    log_file = f"/data/CAST_ext/logs/{user}/{timestamp}.json"

    open(log_file, "w")
    os.chmod(log_file, 0o777)
    # start the log file with an empty array
    with open(log_file, "w") as f:
      json.dump([], f, indent=2)

    
    self.env.update({'LOG_FILE': log_file})
    return await super().start()
    
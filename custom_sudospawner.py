from jupyterhub.spawner import LocalProcessSpawner
import pwd
import subprocess

class SudoSpawner(LocalProcessSpawner):
    async def start(self):
        print(self.user.name)
        user = pwd.getpwnam(self.user.name)
        uid = user.pw_uid
        gid = user.pw_gid
        #self.cmd = ["sudo", "-u", self.user.name, "jupyter", "notebook"]
        #self.process = await self.(cmd, uid=uid, gid=gid)
        return await super().start()
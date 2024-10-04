import os
import json
import base64
import uuid
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class LogExecutionHandler(APIHandler):
  
  @tornado.web.authenticated
  def post(self):
    try:
      data = self.get_json_body()

      log_file = os.getenv("LOG_FILE")
      with open(log_file, 'a') as f:
        f.write(json.dumps(data))
        f.write("\n")  # Ensure each entry is on a new line

      if "outputs" in data.keys():
        self._image_check(data["outputs"])
      

      self.finish(json.dumps({'status': 'success'}))
    except Exception as e:
      self.log.error(f"Error logging execution: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))

  def _image_check(self, outputs):
    cache_dir = os.getenv("CACHE_PATH")
    i = int(len([fname for fname in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir,fname))])/2)
    
    for output in outputs:

      keys_exist = "output_type" in output.keys() and "data" in output.keys()

      if not keys_exist or output["output_type"] != "display_data":
        continue

      data = output["data"]

      if "image/png" not in data.keys():
        continue

      img_str = data["image/png"]
      id = uuid.uuid4()

      with open(os.path.join(cache_dir,f"{id.hex}.png"), "wb") as f:
        f.write(base64.decodebytes(bytes(img_str, "utf-8")))
      
      if "text/plain" not in data.keys():
        continue
      
      with open(os.path.join(cache_dir,f"{id.hex}.txt"), "w") as f:
        f.write(data["text/plain"])

      i += 1


def setup_handlers(web_app):
  host_pattern = '.*$'
  base_url = web_app.settings['base_url']
  route_pattern = url_path_join(base_url, 'log')
  handlers = [(route_pattern, LogExecutionHandler)]
  web_app.add_handlers(host_pattern, handlers)
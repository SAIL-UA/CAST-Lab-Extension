import os
import re
import json
import base64
import uuid
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
import tornado.websocket

class LogExecutionHandler(APIHandler):
  @tornado.web.authenticated
  def post(self):
    try:
      data = self.get_json_body()

      log_file = os.getenv("LOG_FILE")
      with open(log_file, 'a') as f:
        f.write(json.dumps(data))
        f.write("\n")  # Ensure each entry is on a new line

      self.finish(json.dumps({'status': 'success'}))
    except Exception as e:
      self.log.error(f"Error logging execution: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))

class ImageHandler(APIHandler):
  @tornado.web.authenticated
  def post(self):
    try:
      data = self.get_json_body()
      # getting rid of HTML, should use more robust solution eventually
      src = data["src"][22:] 
      cache_dir = os.getenv("CACHE_PATH")
      id = uuid.uuid4().hex
      title_regex = re.compile(r'\.title\("[\S\s]*"\)')

      metadata = {}
      metadata["description"] = "Placeholder Image Description"
      metadata["source"] = ""
      
      with open(os.path.join(cache_dir,f"{id}.png"), "wb") as f:
        f.write(base64.decodebytes(bytes(src, "utf-8")))

      with open(os.path.join(cache_dir,f"{id}.txt"), "w") as f:
        f.write("Placeholder Image Description")

      if "p_code" in data.keys():
        source = data["p_code"]["source"]
        metadata["source"] = source
        m = re.search(title_regex,source)
        if m:
          metadata["description"] = m.group()[8:-2]

      with open(os.path.join(cache_dir,f"{id}.json"), "w") as f:
        json.dump(metadata,f)

      self.finish(json.dumps({'status': 'success'}))
    except Exception as e:
      self.log.error(f"Error saving image: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))



def setup_handlers(web_app):
  host_pattern = '.*$'
  base_url = web_app.settings['base_url']
  
  log_route = url_path_join(base_url, 'log')

  image_route = url_path_join(base_url, 'img')

  handlers = [(log_route, LogExecutionHandler),
              (image_route, ImageHandler)]
  
  web_app.add_handlers(host_pattern, handlers)
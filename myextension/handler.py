from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from jupyterhub.utils import maybe_future
from io import BytesIO
import requests
import tornado
import logging
import base64
import json
import sys
import re
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
  handler = logging.StreamHandler(sys.stdout)
  formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)


class LogExecutionHandler(APIHandler):
  @tornado.web.authenticated
  def post(self):
    """Contains the logic for the POST method of the '/log' API endpoint"""
    try:
      data = self.get_json_body()
      if data is None:
        raise ValueError("No JSON data provided")
      
      # get log file path, which is an environment variable created by the spawner
      log_file = os.getenv("LOG_FILE")
      if log_file is None:
        raise ValueError("LOG_FILE environment variable not set")
      
      # Read existing log entries, add new entry, and write back with proper indentation
      try:
        with open(log_file, 'r') as f:
          log_entries = json.load(f)
      except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/invalid, start with empty list
        log_entries = []
      
      # Add the new entry
      log_entries.append(data)
      
      # Write back with proper indentation (entries indented relative to array)
      with open(log_file, 'w') as f:
        json.dump(log_entries, f, indent=2)

      # we're done
      self.finish(json.dumps({'status': 'success'}))
    except Exception as e:
      self.log.error(f"Error logging execution: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))

class ImageHandler(APIHandler):
  @tornado.web.authenticated
  async def post(self):
    try:
      user = self.current_user
      token = os.environ.get("ACCESS_TOKEN")

      # ✅ Parse image data
      data = self.get_json_body()
      if not data or "src" not in data:
        raise ValueError("Invalid image data")

      base64_image = data["src"].split(",")[1]
      binary_data = base64.b64decode(base64_image)
      file_tuple = ('image.png', BytesIO(binary_data), 'image/png')

      # ✅ Build metadata
      metadata = {
        "short_desc": "Placeholder Image Description",
        "long_desc": "",
        "source": data.get("p_code", {}).get("source", ""),
        "in_storyboard": False,
        "x": 0,
        "y": 0,
        "has_order": False,
        "order_num": 0,
        "last_saved": ""
      }

      title_match = re.search(r'\.title\(["\']([\s\S]*?)["\']\)', metadata["source"])
      if title_match:
        metadata["short_desc"] = title_match.group(1)

      # ✅ POST to Django backend
      response = requests.post(
        "http://backend:8051/api/upload_figure/",
        data=metadata,
        files={"figure": file_tuple},
        headers={"Authorization": f"Bearer {token}"}
      )

      if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code} {response.text}")

      self.finish(json.dumps({'status': 'success'}))

    except Exception as e:
      self.log.error(f"Error in ImageHandler: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))




def setup_handlers(web_app):
  host_pattern = '.*$'
  base_url = web_app.settings['base_url']
  log_route = url_path_join(base_url, 'log')
  image_route = url_path_join(base_url, 'img')
  handlers = [(log_route, LogExecutionHandler),
              (image_route, ImageHandler)]
  
  logger.info(f"Registering handlers at: {handlers}")
  web_app.add_handlers(host_pattern, handlers)

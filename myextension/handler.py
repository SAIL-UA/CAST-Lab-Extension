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
  def post(self):
    """Contains the logic for the POST method of the '/img' API endpoint"""
    try:
      data = self.get_json_body()
      if data is None:
        raise ValueError("No JSON data provided")
        
      # getting rid of HTML, should use more robust solution eventually
      src = data["src"][22:] 
      # get cache directory path from environment variable
      cache_dir = os.getenv("CACHE_PATH")
      if cache_dir is None:
        raise ValueError("CACHE_PATH environment variable not set")
        
      # generate a new universally unique identifier, and get it's hex representation
      id = uuid.uuid4().hex
      # compiles the regular expression to check for a figure title in the code
      title_regex = re.compile(r'\.title\("[\S\s]*"\)')

      # initialize the metadata dictionary
      metadata = {"short_desc": "Placeholder Image Description",
                  "long_desc": "",
                  "source": "",
                  "in_storyboard": False,
                  "x": 0,
                  "y": 0,
                  "has_order": False,
                  "order_num": 0,
                  "last_saved": ""
                  }
      
      # save image to cache
      with open(os.path.join(cache_dir,f"{id}.png"), "wb") as f:
        f.write(base64.decodebytes(bytes(src, "utf-8")))

      # if code cell that output current figure is contained in the "data" dict
      if "p_code" in data.keys():
        # code cell's actual source code
        source = data["p_code"]["source"]
        # give source code to metadata dict
        metadata["source"] = source
        # use the regex compiled earlier in this function to search the source code for a figure title
        m = re.search(title_regex,source)
        # if there is a match
        if m:
          # match is of the form: .title("Figure Title"), so slicing by [8:-2] is consistent
          metadata["short_desc"] = m.group()[8:-2]

      # save json file to the cache
      with open(os.path.join(cache_dir,f"{id}.json"), "w") as f:
        json.dump(metadata,f,indent=4)

      # we're done
      self.finish(json.dumps({'status': 'success'}))
    except Exception as e:
      self.log.error(f"Error saving image: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))



def setup_handlers(web_app):
  """Registers the API handlers at their respective endpoints"""
  host_pattern = '.*$'
  # get base url
  base_url = web_app.settings['base_url']
  
  # join base url + 'log'
  log_route = url_path_join(base_url, 'log')

  # join base url + 'img'
  image_route = url_path_join(base_url, 'img')

  # init handlers list, containing tuples of the form (endpoint, handler)
  handlers = [(log_route, LogExecutionHandler),
              (image_route, ImageHandler)]
  
  # pass the handlers list to the webapp
  web_app.add_handlers(host_pattern, handlers)
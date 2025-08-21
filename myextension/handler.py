from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from io import BytesIO
import tornado
import logging
import base64
import json
import sys
import re
import os
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
  handler = logging.StreamHandler(sys.stdout)
  formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  
BACKEND_URL = os.getenv("STORYSTUDIO_API_URL") or "http://backend:8051/api/"

LOG_UPLOAD_URL    = url_path_join(BACKEND_URL, "jupyter/logs/upload/")
IMAGE_UPLOAD_URL  = url_path_join(BACKEND_URL, "images/upload/")
REFRESH_URL       = url_path_join(BACKEND_URL, "auth/refresh/")


async def _make_async_api_request(method, url, data=None, files=None, headers=None):
  access = os.getenv("ACCESS_TOKEN") or ""
  refresh = os.getenv("REFRESH_TOKEN") or ""

  if not access:
    # synthetic Response so caller logic stays consistent
    return httpx.Response(
      status_code=401,
      headers={"content-type": "application/json"},
      content=json.dumps({"status": "error", "message": "Unauthorized"}),
    )

  async with httpx.AsyncClient(timeout=30.0) as client:
    headers = {**(headers or {}), "Authorization": f"Bearer {access}"}

    # Use json OR form-data, not both. If files provided, send as form-data
    if files:
      resp = await client.request(method, url, data=data, files=files, headers=headers)
    else:
      resp = await client.request(method, url, json=data, headers=headers)

    # One-shot refresh if expired
    if resp.status_code == 401 and refresh:
      rr = await client.post(REFRESH_URL, json={"refresh": refresh})
      if rr.status_code == 200 and "access" in rr.json():
        access = rr.json()["access"]
        headers["Authorization"] = f"Bearer {access}"
        if files:
          resp = await client.request(method, url, data=data, files=files, headers=headers)
        else:
          resp = await client.request(method, url, json=data, headers=headers)

  return resp


class LogExecutionHandler(APIHandler):
  @tornado.web.authenticated
  async def post(self):
    """Contains the logic for the POST method of the '/log' API endpoint"""
    try:
      data = self.get_json_body()
      if data is None:
        raise ValueError("No JSON data provided")
      
      # get request headers
      headers_dict = dict(self.request.headers)
      
      data["request_headers"] = headers_dict
      
      u = self.get_current_user()
      
      username = (
        getattr(u, "name", None)
        or getattr(u, "username", None)
        or (u.get("name") if isinstance(u, dict) else None)
        or (u.get("username") if isinstance(u, dict) else None)
        or (str(u) if u is not None else "")
      )
      
      data["user"] = username
      
      r = await _make_async_api_request("POST", LOG_UPLOAD_URL, data=data)

      if r.status_code not in (200, 201):
        # surface the upstream error instead of 500ing it blindly 
        self.set_status(r.status_code)
        try:
          self.finish(r.json())
        except Exception:
          self.finish({"status": "error", "message": r.text})
        return

      self.finish({"status": "success"})
      
    except Exception as e:
      self.log.error(f"Error logging execution: {e}")
      self.set_status(500)
      self.finish(json.dumps({'status': 'error', 'message': str(e)}))


class ImageHandler(APIHandler):
  @tornado.web.authenticated
  async def post(self):
    try:
      data = self.get_json_body()
      if not data or "src" not in data or "," not in data["src"]:
        raise ValueError("Invalid image data")

      base64_image = data["src"].split(",", 1)[1]
      binary_data = base64.b64decode(base64_image)
      file_tuple = ('image.png', BytesIO(binary_data), 'image/png')
      files = {"figure": file_tuple}

      metadata = {
        "short_desc": "Placeholder Image Description",
        "long_desc": "",
        "source": data.get("p_code", {}).get("source", ""),
        "in_storyboard": False,
        "x": 0, "y": 0,
        "has_order": False, "order_num": 0,
        "last_saved": ""
      }

      m = re.search(r'\.title\(["\']([\s\S]*?)["\']\)', metadata["source"] or "")
      if m:
        metadata["short_desc"] = m.group(1)

      r = await _make_async_api_request("POST", IMAGE_UPLOAD_URL, data=metadata, files=files)

      if r.status_code not in (200, 201):
        # surface the upstream error instead of 500ing it blindly
        self.set_status(r.status_code)
        try:
          self.finish(r.json())
        except Exception:
          self.finish({"status": "error", "message": r.text})
        return

      self.finish({"status": "success"})

    except Exception as e:
      self.log.error(f"Error in ImageHandler: {e}")
      self.set_status(500)
      self.finish({"status": "error", "message": str(e)})



def setup_handlers(web_app):
  host_pattern = '.*$'
  base_url = web_app.settings['base_url']
  log_route = url_path_join(base_url, 'log')
  image_route = url_path_join(base_url, 'img')
  handlers = [(log_route, LogExecutionHandler),
              (image_route, ImageHandler)]
  
  logger.info(f"Registering handlers at: {handlers}")
  web_app.add_handlers(host_pattern, handlers)

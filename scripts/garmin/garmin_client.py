import logging
import os
from enum import Enum, auto


import garth

from garmin_url_dict import GARMIN_URL_DICT

logger = logging.getLogger(__name__)


class GarminClient:
  def __init__(self, email, password, auth_domain):
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.garthClient = garth
  
  ## 登录装饰器
  def login(func):    
    def ware(self, *args, **kwargs):    
      try:
         garth.client.username
      except Exception:
        logger.warning("Garmin is not logging in or the token has expired.")
        if self.auth_domain and str(self.auth_domain).upper() == "CN":
          self.garthClient .configure(domain="garmin.cn")
        self.garthClient.login(self.email, self.password)
      return func(self, *args, **kwargs)
    return ware
  
  @login 
  def download(self, path, **kwargs):
     return self.garthClient.download(path, **kwargs)
  
  @login 
  def connectapi(self, path, **kwargs):
      return self.garthClient.connectapi(path, **kwargs)
     

  ## 获取运动
  def getActivities(self, start:int, limit:int):
     params = {"start": str(start), "limit": str(limit)}
     activities =  self.connectapi(path=GARMIN_URL_DICT["garmin_connect_activities"], params=params)
     return activities;

  ## 获取所有运动
  def getAllActivities(self):
    all_activities = []
    start = 0
    while(True):
      activities = self.getActivities(start=start, limit=100)
      if len(activities) > 0:
         all_activities.extend(activities)
      else:
         return all_activities
      start += 100

  ## 下载原始格式的运动
  def downloadFitActivity(self, activity):
    download_fit_activity_url_prefix = GARMIN_URL_DICT["garmin_connect_fit_download"]
    download_fit_activity_url = f"{download_fit_activity_url_prefix}/{activity}"
    response = self.download(download_fit_activity_url)
    return response

  @login  
  def upload_activity(self, activity_path: str):
    """Upload activity in fit format from file."""
    # This code is borrowed from python-garminconnect-enhanced ;-)

    file_base_name = os.path.basename(activity_path)
    file_extension = file_base_name.split(".")[-1]
    allowed_file_extension = (
        file_extension.upper() in ActivityUploadFormat.__members__
    )

    if allowed_file_extension:
        files = {
            "file": (file_base_name, open(activity_path, "rb" or "r")),
        }
        url = GARMIN_URL_DICT["garmin_connect_upload"]
        return self.garthClient.client.post("connectapi", url, files=files, api=True)
    else:
        pass
  

class ActivityUploadFormat(Enum):
  FIT = auto()
  GPX = auto()
  TCX = auto()

class GarminNoLoginException(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, status):
        """Initialize."""
        super(GarminNoLoginException, self).__init__(status)
        self.status = status


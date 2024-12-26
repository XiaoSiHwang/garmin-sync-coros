import os
import sys 

CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上三级目录
sys.path.append(config_path)

from coros_client import CorosClient
from config  import DB_DIR, COROS_FIT_DIR
from coros_db import CorosDB
from garmin.garmin_client import GarminClient


SYNC_CONFIG = {
    'GARMIN_AUTH_DOMAIN': '',
    'GARMIN_EMAIL': '',
    'GARMIN_PASSWORD': '',
    "COROS_EMAIL": '',
    "COROS_PASSWORD": '',
}

def init(coros_db):
    ## 判断RQ数据库是否存在
    print(os.path.join(DB_DIR, coros_db.coros_db_name))
    if not os.path.exists(os.path.join(DB_DIR, coros_db.coros_db_name)):
        ## 初始化建表
        coros_db.initDB()
    if not os.path.exists(COROS_FIT_DIR):
        os.mkdir(COROS_FIT_DIR)


if __name__ == "__main__":
  # 首先读取 面板变量 或者 github action 运行变量
  for k in SYNC_CONFIG:
      if os.getenv(k):
          v = os.getenv(k)
          SYNC_CONFIG[k] = v

  COROS_EMAIL = SYNC_CONFIG["COROS_EMAIL"]
  COROS_PASSWORD = SYNC_CONFIG["COROS_PASSWORD"]
  corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)

  GARMIN_EMAIL = SYNC_CONFIG["GARMIN_EMAIL"]
  GARMIN_PASSWORD = SYNC_CONFIG["GARMIN_PASSWORD"]
  GARMIN_AUTH_DOMAIN = SYNC_CONFIG["GARMIN_AUTH_DOMAIN"]

  garminClient = GarminClient(GARMIN_EMAIL, GARMIN_PASSWORD, GARMIN_AUTH_DOMAIN)


  ## db 名称
  db_name = "coros.db"
  ## 建立DB链接
  coros_db = CorosDB(db_name)
  ## 初始化DB位置和下载文件位置
  init(coros_db)

  all_activities = corosClient.getAllActivities()
  if all_activities == None or len(all_activities) == 0:
      exit()
  for activity in all_activities:
      activity_id = activity["labelId"]
      sport_type = activity["sportType"]
      coros_db.saveActivity(activity_id, sport_type)



  un_sync_list = coros_db.getUnSyncActivity()
  if un_sync_list == None or len(un_sync_list) == 0:
      exit()
  for un_sync in un_sync_list:
    try:
      id = un_sync["id"]
      sport_type = un_sync["sportType"]
      file = corosClient.downloadActivitie(id, sport_type)
      file_path = os.path.join(COROS_FIT_DIR, f"{id}.fit")
      with open(file_path, "wb") as fb:
          fb.write(file.data)
      upload_status = garminClient.upload_activity(file_path)
      print(f"{id}.fit upload status {upload_status}")
      if upload_status in ("SUCCESS", "DUPLICATE_ACTIVITY"):
        coros_db.updateSyncStatus(id)
      
    except Exception as err:
      print(err)
      coros_db.updateExceptionSyncStatus(un_sync)
      exit()
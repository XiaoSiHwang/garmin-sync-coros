import os
import sys 

import asyncio
CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上三级目录
sys.path.append(config_path)

from config import DB_DIR, GARMIN_FIT_DIR
from garmin.garmin_connect import GarminConnect
from garmin.garmin_db import GarminDB
from coros.coros_client import CorosClient
from coros.entity.login_user import LoginUser



SYNC_CONFIG = {
    'GARMIN_AUTH_DOMAIN': '',
    'GARMIN_EMAIL': '',
    'GARMIN_PASSWORD': '',
    "COROS_EMAIL": '',
    "COROS_PASSWORD": '',
}


def init(stryd_db):
    ## 判断RQ数据库是否存在
    print(os.path.join(DB_DIR, stryd_db.garmin_db_name))
    if not os.path.exists(os.path.join(DB_DIR, stryd_db.garmin_db_name)):
        ## 初始化建表
        stryd_db.initDB()
    if not os.path.exists(GARMIN_FIT_DIR):
        os.mkdir(GARMIN_FIT_DIR)

if __name__ == "__main__":

   # 首先读取 面板变量 或者 github action 运行变量
  for k in SYNC_CONFIG:
      if os.getenv(k):
          v = os.getenv(k)
          SYNC_CONFIG[k] = v
  
  ## db 名称
  db_name = "garmin.db"
  ## 建立DB链接
  garmin_db = GarminDB(db_name)
  ## 初始化DB位置和下载文件位置
  init(garmin_db)

  GARMIN_EMAIL = SYNC_CONFIG["GARMIN_EMAIL"]
  GARMIN_PASSWORD = SYNC_CONFIG["GARMIN_PASSWORD"]
  GARMIN_AUTH_DOMAIN = SYNC_CONFIG["GARMIN_AUTH_DOMAIN"]
  garminConnect = GarminConnect(GARMIN_EMAIL, GARMIN_PASSWORD, GARMIN_AUTH_DOMAIN)

  COROS_EMAIL = SYNC_CONFIG["COROS_EMAIL"]
  COROS_PASSWORD = SYNC_CONFIG["COROS_PASSWORD"]
  corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)
  loop = asyncio.get_event_loop()
  activity_id_list = loop.run_until_complete(garminConnect.get_all_activity_id_list(0))

  for activity_id in activity_id_list:
      garmin_db.saveActivity(activity_id)
  
  un_sync_id_list = garmin_db.getUnSyncActivity()
  for un_sync_id in un_sync_id_list:
    file = loop.run_until_complete(garminConnect.download_activity_fit(un_sync_id))
    file_path = os.path.join(GARMIN_FIT_DIR, f"{un_sync_id}.zip")
    with open(file_path, "wb") as fb:
        fb.write(file)
    upload_result = corosClient.uploadActivity(file_path)
    if upload_result == '0000':
        garmin_db.updateSyncStatus(un_sync_id)
    
import os
from sqlite_db import  SqliteDB
from config import DB_DIR


class GarminDB:
    
    def __init__(self, garmin_db_name):
        ## Garmin数据库
        self._garmin_db_name = garmin_db_name

    @property
    def garmin_db_name(self):
        return self._garmin_db_name

     ## 保存Stryd运动信息
    def saveActivity(self, id):
        exists_select_sql = 'SELECT * FROM garmin_activity WHERE activity_id = ?'
        with SqliteDB(self._garmin_db_name) as db:
            exists_query_set = db.execute(exists_select_sql, (id,)).fetchall()
            query_size = len(exists_query_set)
            if query_size == 0:
              db.execute('insert into garmin_activity (activity_id) values (?)', (id,)) 
    
    def getUnSyncActivity(self):
        select_un_upload_sql = 'SELECT activity_id FROM garmin_activity WHERE is_sync_coros = 0 limit 1000'
        with SqliteDB(self._garmin_db_name) as db:
            un_upload_result = db.execute(select_un_upload_sql).fetchall()
            query_size = len(un_upload_result)
            if query_size == 0:
                return None
            else:
                activity_id_list = []
                for result in un_upload_result:
                    activity_id_list.append(result[0])
                return activity_id_list
            
    def updateSyncStatus(self, activity_id:int):
        update_sql = "update garmin_activity set is_sync_coros = 1 WHERE activity_id = ?"
        with SqliteDB(self._garmin_db_name) as db:
          db.execute(update_sql, (activity_id,))
    
    def updateExceptionSyncStatus(self, activity_id:int):
        update_sql = "update garmin_activity set is_sync_coros = 2 WHERE activity_id = ?"
        with SqliteDB(self._garmin_db_name) as db:
          db.execute(update_sql, (activity_id,))

    def initDB(self):
      with SqliteDB(os.path.join(DB_DIR, self._garmin_db_name)) as db:
          db.execute('''
          
          CREATE TABLE garmin_activity(
              id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT ,
              activity_id INTEGER NOT NULL  , 
              is_sync_coros INTEGER NOT NULL  DEFAULT 0,
              create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          ) 

          '''
          )
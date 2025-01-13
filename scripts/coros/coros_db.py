import os
from sqlite_db import  SqliteDB
from config import DB_DIR


class CorosDB:
    
    def __init__(self, coros_db_name):
        ## 高驰数据库
        self._coros_db_name = coros_db_name

    @property
    def coros_db_name(self):
        return self._coros_db_name

     ## 保存Stryd运动信息
    def saveActivity(self, id, sport_type):
        exists_select_sql = 'SELECT * FROM coros_activity WHERE activity_id = ?'
        with SqliteDB(self._coros_db_name) as db:
            exists_query_set = db.execute(exists_select_sql, (id,)).fetchall()
            query_size = len(exists_query_set)
            if query_size == 0:
              db.execute('insert into coros_activity (activity_id, sport_type) values (?,?)', (id,sport_type)) 
    
    def getUnSyncActivity(self):
        select_un_upload_sql = 'SELECT activity_id,sport_type FROM coros_activity WHERE is_sync_garmin = 0 limit 1000'
        with SqliteDB(self._coros_db_name) as db:
            un_upload_result = db.execute(select_un_upload_sql).fetchall()
            query_size = len(un_upload_result)
            if query_size == 0:
                return None
            else:
                activity_list = []
                for result in un_upload_result:
                    activity = {}
                    activity["id"] = result[0]
                    activity["sportType"] = result[1]
                    activity_list.append(activity)
                return activity_list
            
    def updateSyncStatus(self, activity_id:int):
        update_sql = "update coros_activity set is_sync_garmin = 1 WHERE activity_id = ?"
        with SqliteDB(self._coros_db_name) as db:
          db.execute(update_sql, (activity_id,))
    
    def updateExceptionSyncStatus(self, activity_id:int):
        update_sql = "update coros_activity set is_sync_garmin = 2 WHERE activity_id = ?"
        with SqliteDB(self._coros_db_name) as db:
          db.execute(update_sql, (activity_id,))

    def initDB(self):
      with SqliteDB(os.path.join(DB_DIR, self._coros_db_name)) as db:
          db.execute('''
          
          CREATE TABLE coros_activity(
              id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT ,
              activity_id INTEGER NOT NULL  , 
              sport_type INTEGER NOT NULL  , 
              is_sync_garmin INTEGER NOT NULL  DEFAULT 0,
              create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          ) 

          '''
          )
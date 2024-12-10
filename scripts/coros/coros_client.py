import os

import urllib3
import json
import hashlib

# from entity.login_user import LoginUser



class CorosClient:
    
    def __init__(self, email, password) -> None:
        
        self.email = email
        self.password = password
        self.req = urllib3.PoolManager()
        self.accessToken = None
        self.userId = None
    
    ## 登录接口
    def login(self):
        
        login_url = "https://teamcnapi.coros.com/account/login"

        login_data = {
            "account": self.email,
            "pwd": hashlib.md5(self.password.encode()).hexdigest(), ##MD5加密密码
            "accountType":2,
        }
        headers = {
          "Accept":       "application/json, text/plain, */*",
          "Content-Type": "application/json;charset=UTF-8",
          "User-Agent":   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.39 Safari/537.36",
          "referer": "https://trainingcn.coros.com/",
          "origin": "https://trainingcn.coros.com/",
        }

        login_body = json.dumps(login_data)
        response = self.req.request('POST', login_url, body=login_body, headers=headers)

        login_response = json.loads(response.data)
        login_result = login_response["result"]
        if login_result != "0000":
            raise CorosLoginError("高驰登录异常，异常原因为：" + login_response["message"])

        accessToken = login_response["data"]["accessToken"]
        userId =  login_response["data"]["userId"]
        self.accessToken = accessToken
        self.userId = userId

    ## 上传运动
    def uploadActivity(self, oss_object, md5, fileName):
        ## 判断Token 是否为空
        if self.accessToken == None:
            self.login()

        upload_url = "https://teamcnapi.coros.com/activity/fit/import"

        headers = {
          "Accept":       "application/json, text/plain, */*",
          "accesstoken": self.accessToken,
        }
     
        try:

          data = {"source":1,"timezone":32,"bucket":"coros-oss","md5":f"{md5}","size":0,"object":f"{oss_object}","serviceName":"aliyun","oriFileName":f"{fileName}"}
          
          json_data = json.dumps(data)
          json_str = str(json_data)
          response = self.req.request(
              method = 'POST',
              url=upload_url,
              fields={ "jsonParameter": json_str},
              headers=headers
          )
          upload_response = json.loads(response.data)
          upload_result = upload_response["result"]
          return upload_result
        except Exception as err:
            exit() 


class CorosLoginError(Exception):

    def __init__(self, status):
        """Initialize."""
        super(CorosLoginError, self).__init__(status)
        self.status = status

class CorosActivityUploadError(Exception):

    def __init__(self, status):
        """Initialize."""
        super(CorosActivityUploadError, self).__init__(status)
        self.status = status


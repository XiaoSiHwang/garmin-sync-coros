import logging
import os
import sys 
import re

CURRENT_DIR = os.path.split(os.path.abspath(__file__))[0]  # 当前目录
config_path = CURRENT_DIR.rsplit('/', 1)[0]  # 上三级目录
sys.path.append(config_path)

import json
import cloudscraper
import httpx

logger = logging.getLogger(__name__)
TIME_OUT = httpx.Timeout(240.0, connect=360.0)

GARMIN_COM_URL_DICT = {
    "BASE_URL": "https://connect.garmin.com",
    "SSO_URL_ORIGIN": "https://sso.garmin.com",
    "SSO_URL": "https://sso.garmin.com/sso",
    "MODERN_URL": "https://connect.garmin.com",
    "SIGNIN_URL": "https://sso.garmin.com/sso/signin",
    "CSS_URL": "https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css",
    "UPLOAD_URL": "https://connect.garmin.com/modern/proxy/upload-service/upload/.gpx",
    "ACTIVITY_URL": "https://connect.garmin.com/proxy/activity-service/activity/{activity_id}",
}

GARMIN_CN_URL_DICT = {
    "BASE_URL": "https://connect.garmin.cn",
    "SSO_URL_ORIGIN": "https://sso.garmin.com",
    "SSO_URL": "https://sso.garmin.cn/sso",
    "MODERN_URL": "https://connect.garmin.cn",
    "SIGNIN_URL": "https://sso.garmin.cn/sso/signin",
    "CSS_URL": "https://static.garmincdn.cn/cn.garmin.connect/ui/css/gauth-custom-v1.2-min.css",
    "UPLOAD_URL": "https://connect.garmin.cn/modern/proxy/upload-service/upload/.gpx",
    "ACTIVITY_URL": "https://connect.garmin.cn/proxy/activity-service/activity/{activity_id}",
}


class GarminConnect:
    def __init__(self, email, password, auth_domain, is_only_running=False):
        """
        Init module
        """
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.req = httpx.AsyncClient(timeout=TIME_OUT)
        self.cf_req = cloudscraper.CloudScraper()
        self.URL_DICT = (
            GARMIN_CN_URL_DICT
            if auth_domain and str(auth_domain).upper() == "CN"
            else GARMIN_COM_URL_DICT
        )
        self.modern_url = self.URL_DICT.get("MODERN_URL")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "origin": self.URL_DICT.get("SSO_URL_ORIGIN"),
            "nk": "NT",
        }
        self.is_only_running = is_only_running
        self.upload_url = self.URL_DICT.get("UPLOAD_URL")
        self.activity_url = self.URL_DICT.get("ACTIVITY_URL")
        self.is_login = False

    def login(self):
        """
        Login to portal
        """
        params = {
            "webhost": self.URL_DICT.get("BASE_URL"),
            "service": self.modern_url,
            "source": self.URL_DICT.get("SIGNIN_URL"),
            "redirectAfterAccountLoginUrl": self.modern_url,
            "redirectAfterAccountCreationUrl": self.modern_url,
            "gauthHost": self.URL_DICT.get("SSO_URL"),
            "locale": "en_US",
            "id": "gauth-widget",
            "cssUrl": self.URL_DICT.get("CSS_URL"),
            "clientId": "GarminConnect",
            "rememberMeShown": "true",
            "rememberMeChecked": "false",
            "createAccountShown": "true",
            "openCreateAccount": "false",
            "usernameShown": "false",
            "displayNameShown": "false",
            "consumeServiceTicket": "false",
            "initialFocus": "true",
            "embedWidget": "false",
            "generateExtraServiceTicket": "false",
        }

        data = {
            "username": self.email,
            "password": self.password,
            "embed": "true",
            "lt": "e1s1",
            "_eventId": "submit",
            "displayNameRequired": "false",
        }

        try:
            self.cf_req.get(
                self.URL_DICT.get("SIGNIN_URL"), headers=self.headers, params=params
            )
            response = self.cf_req.post(
                self.URL_DICT.get("SIGNIN_URL"),
                headers=self.headers,
                params=params,
                data=data,
            )
        except Exception as err:
            raise GarminConnectConnectionError("Error connecting") from err
        response_url = re.search(r'"(https:[^"]+?ticket=[^"]+)"', response.text)

        if not response_url:
            raise GarminConnectAuthenticationError("Authentication error")

        response_url = re.sub(r"\\", "", response_url.group(1))
        try:
            response = self.cf_req.get(response_url)
            self.req.cookies = self.cf_req.cookies
            if response.status_code == 429:
                raise GarminConnectTooManyRequestsError("Too many requests")
            response.raise_for_status()
            self.is_login = True
        except Exception as err:
            raise GarminConnectConnectionError("Error connecting") from err
    
    async def upload_activities(self, file_path):
        try:
          status = None
          if not self.is_login:
              self.login()
          file_type = os.path.splitext(file_path)[-1]
          upload_url = f"{self.modern_url}/proxy/upload-service/upload/{file_type}"
          files = {"data": (f"file{file_type}", open(file_path, 'rb'))}
          try:
            res = await self.req.post(
                upload_url, files=files, headers={"nk": "NT"}
            )
          except Exception as e:
            print(e)
            raise Exception("failed to upload")
          result_json = json.loads(res.text)
          print(result_json)
          res_code = res.status_code
          uploadId =  result_json.get("detailedImportResult").get('uploadId')
          isDuplicateUpload = uploadId == None or uploadId == ''
          if res_code == 202 and not isDuplicateUpload:
              status = "SUCCESS"
          elif res_code == 409 and result_json.get("detailedImportResult").get("failures")[0].get('messages')[0].get('content') == "Duplicate Activity.":
              status = "DUPLICATE_ACTIVITY" 
        except Exception as e:
            status = "UPLOAD_EXCEPTION"
        finally:
            return status

    async def get_activitys(self, limit, start):
        if not self.is_login:
            self.login()
        url = f"{self.modern_url}/proxy/activitylist-service/activities/search/activities?start={start}&limit={limit}"
        return await self.featch_get_request_data(url)

    async def featch_get_request_data(self, url):
        try:
            response = await self.req.get(
            url,
            headers=self.headers
        )
            if response.status_code == 429:
                print("429")
            logger.debug(f"fetch_data got response code {response.status_code}")
            response.raise_for_status()
            return response.json()
        except Exception as err:
            raise err
    async def download_activity_fit(self, activity_id):
        if not self.is_login:
            self.login()
        url = f"{self.modern_url}/proxy/download-service/files/activity/{activity_id}"
        logger.info(f"Download activity from {url}")
        response = await self.req.get(url, headers=self.headers)
        response.raise_for_status()
        return response.read()
    
    async def get_all_activity_id_list(self, start):
        respone = await self.get_activitys(100, start)
        if len(respone) > 0:
            activity_list = []
            for result in respone:
                activity_list.append(result.get("activityId"))
            return activity_list + await self.get_all_activity_id_list(start + 100)
        else:
            return []




class GarminConnectHttpError(Exception):
    def __init__(self, status):
        super(GarminConnectHttpError, self).__init__(status)
        self.status = status


class GarminConnectConnectionError(Exception):
    """Raised when communication ended in error."""

    def __init__(self, status):
        """Initialize."""
        super(GarminConnectConnectionError, self).__init__(status)
        self.status = status


class GarminConnectTooManyRequestsError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, status):
        """Initialize."""
        super(GarminConnectTooManyRequestsError, self).__init__(status)
        self.status = status


class GarminConnectAuthenticationError(Exception):
    """Raised when login returns wrong result."""

    def __init__(self, status):
        """Initialize."""
        super(GarminConnectAuthenticationError, self).__init__(status)
        self.status = status
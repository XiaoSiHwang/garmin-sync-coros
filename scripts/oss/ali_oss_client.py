import urllib3
import json
import oss2
import os
import certifi

from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
from utils.coros_oss_credients_utils import decode


class AliOssClient:
    def __init__(self, bucket="coros-oss", service="aliyun", app_id="1660188068672619112", sign="9AD4AA35AAFEE6BB1E847A76848D58DF", v=2):
        self.bucket = bucket
        self.service = service
        self.app_id = app_id
        self.sign = sign
        self.security_token = None
        self.access_key_id = None
        self.access_key_secret = None
        self.req = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.client = None
        self.v = v
        self.initClient()

    def initClient(self):
        sts_token_url = f"https://faq.coros.com/openapi/oss/sts?bucket={self.bucket}&service={self.service}&app_id={self.app_id}&sign={self.sign}&v={self.v}"

        response = self.req.request('GET', sts_token_url)

        sts_token_response = json.loads(response.data)
        if sts_token_response["code"] != 200:
            raise StsTokenError("获取阿里云OSS STS Token异常")
        credentials = sts_token_response["data"]["credentials"]
        credients_json = decode(credentials)


        SecurityToken = credients_json["SecurityToken"]
        AccessKeyId = credients_json["AccessKeyId"]
        AccessKeySecret = credients_json["AccessKeySecret"]
        self.security_token = SecurityToken
        self.access_key_id = AccessKeyId
        self.access_key_secret = AccessKeySecret

        auth = oss2.StsAuth(self.access_key_id, self.access_key_secret, self.security_token)
        self.client = oss2.Bucket(auth, "https://oss-cn-beijing.aliyuncs.com", self.bucket)
    
    def multipart_upload(self, filePath, fileName):
        key = f"fit_zip/{fileName}"
        print(key)
        init_multipart_upload_result = self.client.init_multipart_upload(key)
        if init_multipart_upload_result.status != 200:
            raise AliOssError("初始化阿里云分片上传异常")
        upload_id = init_multipart_upload_result.upload_id
        total_size = os.path.getsize(filePath)
        # determine_part_size方法用于确定分片大小。
        part_size = determine_part_size(total_size, preferred_size=1024 * 1024)
        parts = []

        # 逐个上传分片。
        with open(filePath, 'rb') as fileobj:
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = self.client.upload_part(key, upload_id, part_number,
                                            SizedFileAdapter(fileobj, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

        # 完成分片上传。
        # 如需在完成分片上传时设置相关Headers，请参考如下示例代码。
        headers = dict()
        # 设置文件访问权限ACL。此处设置为OBJECT_ACL_PRIVATE，表示私有权限。
        # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
        r = self.client.complete_multipart_upload(key, upload_id, parts, headers=headers)
        return key
    



class StsTokenError(Exception):

    def __init__(self, status):
        """Initialize."""
        super(StsTokenError, self).__init__(status)
        self.status = status

class AliOssError(Exception):
    def __init__(self, status):
      """Initialize."""
      super(AliOssError, self).__init__(status)
      self.status = status
from scripts.coros.coros_client import CorosClient
from scripts.utils.md5_utils import calculate_md5_file
from scripts.oss.ali_oss_client import AliOssClient

COROS_EMAIL = ''
COROS_PASSWORD = ''
corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)
corosClient.login()
print(corosClient.userId)
# corosClient.uploadActivity("fit_zip/58a0fa43058a4aaf84d2564ead944271.fit", calculate_md5_file("garmin-fit/58a0fa43058a4aaf84d2564ead944271.fit"), "58a0fa43058a4aaf84d2564ead944271.fit")
client = AliOssClient()
file_path = 'garmin-fit/17979659691.zip'
import os
size = os.path.getsize(file_path) # 文件路径及文件名
print(size)
oss_obj = client.multipart_upload(file_path, f"{corosClient.userId}/{calculate_md5_file(file_path)}.zip")
upload_result = corosClient.uploadActivity(f"fit_zip/{corosClient.userId}/{calculate_md5_file(file_path)}.zip", calculate_md5_file(file_path), "17979659691.zip", size)


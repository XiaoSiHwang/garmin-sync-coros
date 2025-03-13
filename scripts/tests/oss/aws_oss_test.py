from scripts.coros.coros_client import CorosClient
from scripts.utils.md5_utils import calculate_md5_file

COROS_EMAIL = ''
COROS_PASSWORD = ''
corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)
corosClient.login()

import boto3

import base64

import json
from boto3.s3.transfer import TransferConfig


# 假设 salt_encode_credient 是被“盐”保护的加密字符串，salt 是盐值
salt_encode_credient = "eyJBY2Nlc3NLZXlJZCI6IkFTSUFTTU1TSTVVWkg3NklIRVJTIiwiU2VjcmV0QWNjZXNzS2V5IjoieFFtTURjVSsyU0d6SWJldlNENS8ybjdQdlNXUXZ0TmY5bjVuWU81WSIsIlNlc3Npb25Ub2tlbiI6IklRb0piM0pwWjJsdVgyVmpFTmIvLy8vLy8vLy8vd0VhREdWMUxXTmxiblJ5WVd3dE1TSkdNRVFDSUU3blJqTDdiYTlWcEk2MGoydXZxdFlDM0VQTVUyelZHeEdGc2tGUDRGY2RBaUJYWm9KcDV1S0tpRmdWQzdNWXUwa1NIQ0U0YVh6N3djREVCZTBlN1FzdUlTcnpBUWovLy8vLy8vLy8vLzhCRUFBYURERTJOREExTWpNNU56TTJNaUlNbWdsQnJBNFpiTDJ0ZjYzbEtzY0JpOEo3RWMzUTByR3VUblpjTWpsNytPWnI1VGlVTFV3S21XYVczeEpuaExXZ3A1emxVaERaNm50RlBmUWZvN0Ftb01uVE9UalVERGE4b1dLSlFDaUJ2Z0dlTHJJY1ZrVDRXY2FpOEx2TVEzRnQ1S0F2SGRURHIyMEFYdUlUb2RFai8ySm94RkVjb1JWTE43SjN0Z3NHU1puY2VLZDJMM0N0ZWExTlYwc2xGYk8zK3J2SCs4bHV6ZmEySDhUbG5wTVV5d09tOS9CTEVuTk5ndXF5cTYwdEtwWE43cXg3V3c4dHo3S2crKzhoMlhQNnR2emY4STdQL0xOK2RQZEhqQzMxMGEvcUdaYkkrRENpK2VxOUJqcVpBWDUzMzdrenJINUlmNnlJNm1zcDU4MEdnMmc0K3VpNWZoQTByblgvd2oxczdiOG5MMTZkcVJBaEJIaHA3ZUlWejBxT1F3cWhsUWduQ3FEZ1BGTGQ0VjlueitlS1dBTTUzZWV6UEdMVGdscTNsR0tXRy9rMmNrUDZwamdmR1NSdHhJQXVrQ1BpVEhtVjlhdmM2TjVOUU1qQWg0UkFHWHJlNFhrUlc4amdHRWQ2YVdaK0dzVXVqUk84NnZZSHhLVFZtazhTRUNQRmFnQmJyUT09IiwiRXhwaXJhdGlvbiI6IjIwMjUtMDItMjNUMDc6MTM6NTQuMDAwWiIsIlRva2VuRXhwaXJlVGltZSI6MzYwMCwiUmVnaW9uIjoiZXUtY2VudHJhbC0xIiwiQnVja2V0IjoiZXUtY29yb3MiLCJTZXNzaW9uTmFtZSI6ImV1LWNvcm9zX2MzMGVmNGY5ZTEzOTRjYjdiYTkyN2ZhYzAxMGE2Y2NiIiwiQWNjZXNzS2V5U2VjcmV0IjoieFFtTURjVSsyU0d6SWJldlNENS8ybjdQdlNXUXZ0TmY5bjVuWU81WSJ99y78gpoERW4lBNYL"
salt = "9y78gpoERW4lBNYL"  # 盐值

# 第一步：去除盐（salt）部分
encode_credient = salt_encode_credient.replace(salt, '')

# 第二步：Base64 解码
credients = base64.b64decode(encode_credient).decode('utf-8')  # 解码后的内容转成 utf-8 字符串

credients_json = json.loads(credients)
print(credients_json["SessionToken"])


s3_client = boto3.client(
    "s3",
    aws_access_key_id=credients_json["AccessKeyId"],
    aws_secret_access_key=credients_json["SecretAccessKey"],
    aws_session_token=credients_json["SessionToken"],
    endpoint_url='https://s3.eu-central-1.amazonaws.com',
)
file_path = 'garmin-fit/17969597203.zip'

# 配置上传选项
config = TransferConfig(
    multipart_threshold=1024 * 1024 * 5,  # 分片上传的阈值（5MB）
    max_concurrency=4,                   # 并发数
    multipart_chunksize=1024 * 1024 * 5,  # 分片大小（5MB）
    use_threads=True                     # 使用多线程
)

# 执行上传
try:
    s3_client.upload_file(
        file_path,
          Bucket=credients_json["Bucket"],
        Key=f"fit_zip/{corosClient.userId}/{calculate_md5_file(file_path)}.zip",
        Config=config
    )
    print("File uploaded successfully!")
except Exception as e:
    print(f"Upload failed: {e}")
import os
size = os.path.getsize(file_path) # 文件路径及文件名

upload_result = corosClient.uploadActivity(f"fit_zip/{corosClient.userId}/{calculate_md5_file(file_path)}.zip", calculate_md5_file(file_path), "18008793949.zip", size)

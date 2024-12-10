from scripts.coros.coros_client import CorosClient
from scripts.utils.md5_utils import calculate_md5_file
COROS_EMAIL = ''
COROS_PASSWORD = ''
corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)
corosClient.login()
print(corosClient.accessToken)
corosClient.uploadActivity("fit_zip/17713098018.zip", calculate_md5_file("garmin-fit/17601184069.zip"), "17601184069.zip")
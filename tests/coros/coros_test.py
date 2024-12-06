from scripts.coros.coros_client import CorosClient
COROS_EMAIL = ''
COROS_PASSWORD = ''
corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)
corosClient.login()
print(corosClient.accessToken)
corosClient.uploadActivity("fit_zip/17601771625.zip")
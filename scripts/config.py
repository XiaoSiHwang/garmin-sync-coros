import os

SYS_CONFIG = {}

# 首先读取 面板变量 或者 github action 运行变量
for k in SYS_CONFIG:
    if os.getenv(k):
        v = os.getenv(k)
        SYS_CONFIG[k] = v

# getting content root directory
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)


GARMIN_FIT_DIR = os.path.join(parent, "garmin-fit")
COROS_FIT_DIR = os.path.join(parent, "coros-fit")

DB_DIR =  os.path.join(parent, "db")

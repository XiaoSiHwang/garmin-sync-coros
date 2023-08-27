# Sport Sync 同步程序是过渡DailySync 作者还未推出Web版本而开发，[DailySync](https://github.com/gooin)作者推出新项目后大力推荐大家使用DailySync作者推出的新项目而非本项目（由于Github Action政策本项目很大概率会被Ban😁😁）

## Feature
- Garmin双向同步（国区->国际区）（国际区->国区）（国区->国区）（国际区->国际区）
- Garmin同步时坚果云异地备份运动数据 （**可支持不使用坚果云保存简化配置**）
- RQ RUN 签到
- 各种消息推送（企业微信机器人，钉钉，Bark。。。。）目前只配置了企业微信机器人


文档: 📖 [Sport Sync Docs](https://blog.999973.xyz/1430702270/)
## 配置参数
|  参数名   | 备注  |是否必填|
|  ----  | ----  |----  |
| LOCAL_OR_WEBDAV  | 使用Github Action存储填False 使用坚果云保存填True | 是|
| AESKEY  | AES KEY用于加密数据 | 是|
| QYWX_KEY  | 企业微信机器人KEY | 否|
| DD_BOT_SECRET  | 叮叮机器人SECRET | 否|
| DD_BOT_TOKEN  | 叮叮机器人TOKEN | 否|
| RQ_EMAIL  | RQ帐号 | 是|
| RQ_PASSWORD  | RQ密码 | 是|
| SOURCE_GARMIN_AUTH_DOMAIN  | 主Garmin域（国区填cn 国际区填com) | 是|
| SOURCE_GARMIN_EMAIL  | 主Garmin的Email | 是|
| SOURCE_GARMIN_PASSWORD  | 主Garmin的Password | 是|
| SYNC_GARMIN_AUTH_DOMAIN  | 同步Garmin域（国区填cn 国际区填com) | 是|
| SYNC_GARMIN_EMAIL  | 同步Garmin的Email | 是|
| SYNC_GARMIN_PASSWORD  | 同步Garmin的PASSWORD  | 是|
| WEBDAV_URL  | 坚果云服务器地址 | 是|
| WEBDAV_USERNAME  | 坚果云帐号 | 是|
| WEBDAV_PASSWORD  | 坚果云WEBDAV密钥 | 是|




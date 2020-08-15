# linebot-heroku

### 開發前準備事項
- [Heroku](https://dashboard.heroku.com/apps) 帳戶（free)
- 透過 Line 帳號登入[LINE Developers](https://developers.line.biz/console/)建立一個專案
- 透過 Line 帳號登入[LINE official Account Manager](https://manager.line.biz/)

### 將 Line bot 串接到 Heroku 伺服器
1. 點擊 **Messaging API** 進入 API 設定頁面
   1. 透過上面的 QR code 將機器人加入好友

###
- Procfile：
- TODO:改用 gunicorn 這個 WSGI Server。${flask_app} 為檔案模組名稱、${app} 為檔案中 Flask app 的 instance。
   ```bash
   web: gunicorn ${flask_app}:${app} –log-file -
   ```
- runtime.txt：Python 版本，使用 python-3.6.8
- requirements.txt

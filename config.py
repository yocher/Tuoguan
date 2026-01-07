import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'Z8DguWnb')
db_address = os.environ.get("MYSQL_ADDRESS", 'sh-cynosdbmysql-grp-g1viz1sm.sql.tencentcdb.com:25808')

# Session配置
SECRET_KEY = os.environ.get("SECRET_KEY", 'sk-tuoguan2026')

# 微信配置
WECHAT_APPID = os.environ.get('WECHAT_APPID', '')
WECHAT_SECRET = os.environ.get('WECHAT_SECRET', '')
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', '')
WECHAT_TEMPLATE_ID = os.environ.get('WECHAT_TEMPLATE_ID', '')
MINIPROGRAM_APPID = os.environ.get('MINIPROGRAM_APPID', '')

# 文件上传配置
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

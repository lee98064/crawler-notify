from environs import Env

env = Env()
env.read_env()

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = env.str("TELEGRAM_API_URL", default="https://api.telegram.org")

# 預設每10秒1次
JOB_EXECUTION_INTERVAL = env.int("JOB_EXECUTION_INTERVAL", default=10) 
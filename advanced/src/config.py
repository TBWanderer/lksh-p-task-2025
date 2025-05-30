import os
from datetime import datetime

class Config:
    BASE_API_URL = "https://lksh-enter.ru"
    TOKEN = os.getenv("LKSH_P_AUTH_TOKEN")
    CACHE_FILE = "cache.json"
    LOG_DIR = "logs"
    LOG_FILENAME = os.path.join(LOG_DIR, f"{datetime.now():%Y-%m-%d}.log")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

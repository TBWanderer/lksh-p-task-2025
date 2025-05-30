import os
import sys

class Config:
    BASE_API_URL = "https://lksh-enter.ru"
    TOKEN = os.getenv("LKSH_P_AUTH_TOKEN")
    CACHE_FILE = "cache.json"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

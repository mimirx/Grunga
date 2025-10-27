import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "grunga"),
}

APP_TZ = os.getenv("TZ", "America/Chicago")

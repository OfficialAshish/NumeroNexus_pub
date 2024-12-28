import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
DATABASE_URL = os.getenv("DATABASE_URL")

GEO_API_KEY = os.getenv("GEO_API_KEY")
JWT_KEY = os.getenv("JWT_SECRET_KEY")
DB_SECRET_KEY = os.getenv("DB_SECRET_KEY")

# Initialize Redis client
REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
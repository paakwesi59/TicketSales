# config.py
import os

class Config:
    # SECRET_KEY must be set in the environment
    SECRET_KEY = os.environ["SECRET_KEY"]

    # MySQL Database Configuration
    MYSQL_USER = os.environ["MYSQL_USER"]
    MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_DB = os.environ["MYSQL_DB"]
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Configuration (Using Gmail in this example)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)


# Debug print statements
    print(f"Loaded MAIL_SERVER: {MAIL_SERVER}")
    print(f"Loaded MAIL_PORT: {MAIL_PORT}")
    print(f"Loaded MAIL_USE_TLS: {MAIL_USE_TLS}")
    print(f"Loaded MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"Loaded MAIL_PASSWORD: {MAIL_PASSWORD}")
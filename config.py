import os

class Config:
    # General Flask Configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"

    # MySQL Database Configuration
    MYSQL_USER = os.environ.get("MYSQL_USER") or "root"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or "Dontworry303"
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or "localhost"
    MYSQL_DB = os.environ.get("MYSQL_DB") or "ticket_sales_db"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration (for production, update these values)
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False  # Typically False when using TLS on port 587
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "asmahpaakwesi59@gmail.com"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or "rwyp egon cawm bzih"
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or "asmahpaakwesi59@gmail.com"

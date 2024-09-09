import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    ADMIN_KEY = os.environ.get("ADMIN_KEY")
    DB_HOST = os.environ.get("HOST")
    DB_USER = os.environ.get("USER")
    DB_PASSWORD = os.environ.get("PASSWORD")
    DB_DATABASE = os.environ.get("DATABASE")
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_CONFIG = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/{}.json'.format('apispec_1'),
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/swagger/"
    }
    MAIL_BODY = """<!DOCTYPE html>
                <html lang="tr">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Elektrik Bağlantı Sorunu Hakkında Bilgilendirme</title>
                </head>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #d9534f;">Dikkat!</h2>
                        <p>Değerli Kullanıcımız,</p>
                        <p>Bir süredir elektrik bağlantınıza ulaşamadığımızı fark ettik. Bu durumun çözülmesi için lütfen bağlantınızı kontrol edin ve sorunun devam etmesi halinde bizimle iletişime geçin.</p>
                        <p>Herhangi bir sorunuz olursa size yardımcı olmaktan memnuniyet duyarız.</p>
                    </div>
                </body>
                </html>
                """

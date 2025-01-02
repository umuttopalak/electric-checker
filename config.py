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
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMIN_KEY = os.environ.get('ADMIN_KEY')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {
        'title': 'Electric Checker API',
        'uiversion': 3,
        'specs_route': '/swagger/',
        'openapi': '3.0.2',
        'static_url_path': '/flasgger_static',
        'swagger_ui': True
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

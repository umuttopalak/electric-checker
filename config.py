import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    ADMIN_KEY = os.environ.get("ADMIN_KEY")
    DB_HOST = os.environ.get("HOST")
    DB_USER = os.environ.get("USER")
    DB_PASSWORD = os.environ.get("PASSWORD")
    DB_DATABASE = os.environ.get("DATABASE")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
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

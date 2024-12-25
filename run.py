from app import create_app, db
from flask_migrate import upgrade

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        upgrade()
    app.run(host='0.0.0.0', port=3000) 
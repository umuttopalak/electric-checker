
# Electric Check Flask Application

This Flask application allows users to check their electric status, register with a license, and perform various admin operations, such as activating/deactivating licenses, user management, and sending notifications via email and Telegram.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Technologies](#technologies)
- [Swagger Documentation](#swagger-documentation)

## Installation

To run this project locally, follow the instructions below.

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- PostgreSQL (or any SQLAlchemy compatible database)
- A Telegram bot token (for notifications)
- SMTP settings for sending emails

### Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Install dependencies

It's recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Set up your database

Make sure PostgreSQL (or your chosen database) is installed and running. Configure your database connection string in the `config.py` file:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://<username>:<password>@<host>:<port>/<database>'
```

Then, run the migrations to set up the database:

```bash
flask db upgrade
```

## Configuration

The application relies on the `config.py` file for configuration. Below are some important configuration parameters you need to set:

- `SQLALCHEMY_DATABASE_URI`: Database connection string.
- `MAIL_DEFAULT_SENDER`: Default email sender address.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email server configurations for sending notifications.
- `TELEGRAM_TOKEN`: Telegram bot token for sending messages.
- `ADMIN_KEY`: Key for admin operations.

## Usage

### Running the application

To run the application, use the following command:

```bash
python app.py
```

The application will run on `http://localhost:3000` by default.

### Running the app with Docker

Alternatively, you can use Docker:

```bash
docker build -t electric-check-app .
docker run -p 3000:3000 electric-check-app
```

## Endpoints

### Public Endpoints

- `GET /health-check`: Health check to verify if the system is working.
- `POST /user/electric-check`: Check the electric status of a user.
- `GET /user/electric-check`: Retrieve the last request date for a user.

### Admin Endpoints

All admin endpoints require an `admin-key` in the request headers:

- `GET /admin/users/list`: Get a list of all registered users.
- `POST /admin/users/register`: Register a new user.
- `DELETE /admin/users/delete/`: Delete a user by email.
- `PATCH /admin/license/deactivate/<username>`: Deactivate a user's license.
- `PATCH /admin/license/activate/<username>`: Activate a user's license.
- `GET /admin/periodic-check`: Run a check for users who haven't made a request recently and send a notification.

### Telegram Endpoints

- `POST /telegram/user-data`: Create a user based on data received from the Telegram bot.

## Technologies

- **Flask**: Web framework for Python.
- **SQLAlchemy**: ORM for database interaction.
- **Flask-Migrate**: Handles database migrations.
- **Flask-Mail**: Sending emails.
- **APScheduler**: Scheduling tasks.
- **Telegram Bot API**: For sending notifications via Telegram.
- **Flasgger**: Swagger API documentation for Flask.

## Swagger Documentation

This project uses Swagger to provide API documentation. After starting the application, visit:

```
http://localhost:3000/apidocs/
```

This will allow you to view and interact with the API endpoints using the Swagger UI.

## License

This project is licensed under the MIT License.
```

from app import db
import uuid

class User(db.Model):
    username = db.Column(db.String(36), primary_key=True, unique=True,
                        nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    last_request_date = db.Column(db.DateTime, nullable=True)
    has_license = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    chat_id = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "last_request_date": None if self.last_request_date is None else self.last_request_date.isoformat(),
            "has_license": True if self.has_license else False,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "chat_id": self.chat_id,
        } 
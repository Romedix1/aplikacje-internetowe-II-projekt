from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    index_number = db.Column(db.String(20), unique=True)
    auth_provider = db.Column(db.String(50), default="microsoft")
    external_id = db.Column(db.String(255), unique=True)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    study_field = db.Column(db.String(100), nullable=True)
    study_year = db.Column(db.String(20), nullable=True)
    study_form = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.Integer, nullable=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_id(self):
        return str(self.id)

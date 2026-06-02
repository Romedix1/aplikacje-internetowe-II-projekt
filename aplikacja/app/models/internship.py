from app.models.user import db


class Internship(db.Model):
    __tablename__ = "internship"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uopz_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    zopz_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    company_name = db.Column(db.String(255), nullable=False)
    company_address = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    working_days = db.Column(db.Integer, nullable=False, default=120)
    status = db.Column(db.String(50), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    diaries = db.relationship(
        "Diary", backref="internship", cascade="all, delete-orphan", lazy=True
    )

    documents = db.relationship(
        "Document", backref="internship", cascade="all, delete-orphan", lazy=True
    )

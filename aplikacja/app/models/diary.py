from app.models.user import db


class Diary(db.Model):
    __tablename__ = "diary"

    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(
        db.Integer, db.ForeignKey("internship.id"), nullable=False, unique=True
    )
    status = db.Column(db.String(50), nullable=False, default="draft")
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    entries = db.relationship(
        "DiaryEntry", backref="diary", lazy=True, cascade="all, delete-orphan"
    )


class DiaryEntry(db.Model):
    __tablename__ = "diary_entry"

    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey("diary.id"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    outcome_numbers = db.Column(db.String(50))
    confirmed_by_zopz = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime)
    is_rejected = db.Column(db.Boolean, default=False, nullable=False)

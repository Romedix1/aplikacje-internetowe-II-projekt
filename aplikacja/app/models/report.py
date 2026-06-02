from app.models.user import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(
        db.Integer, db.ForeignKey("internship.id"), nullable=False
    )
    company_description = db.Column(db.Text, nullable=True)
    work_description = db.Column(db.Text, nullable=True)
    self_assessment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="draft")
    submitted_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

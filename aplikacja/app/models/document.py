from app.models.user import db


class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(
        db.Integer, db.ForeignKey("internship.id"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="draft")
    submitted_at = db.Column(db.DateTime)
    supervisor_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

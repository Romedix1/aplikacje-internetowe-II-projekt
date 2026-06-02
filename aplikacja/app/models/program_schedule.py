from app.models.user import db


class ProgramSchedule(db.Model):
    __tablename__ = "program_schedule"
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(
        db.Integer, db.ForeignKey("internship.id"), nullable=False, unique=True
    )
    agreed_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="draft", nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    entries = db.relationship(
        "ScheduleEntry", backref="program", lazy=True, cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "ProgramTask", backref="program", lazy=True, cascade="all, delete-orphan"
    )


class ScheduleEntry(db.Model):
    __tablename__ = "schedule_entry"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(
        db.Integer, db.ForeignKey("program_schedule.id"), nullable=False
    )
    lp = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(255), nullable=False)
    planned_days = db.Column(db.Integer, nullable=False)


class ProgramTask(db.Model):
    __tablename__ = "program_task"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(
        db.Integer, db.ForeignKey("program_schedule.id"), nullable=False
    )
    outcome_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False, default="")

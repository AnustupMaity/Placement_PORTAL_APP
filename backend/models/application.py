""" std appn to pd """

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from extensions import db

class Application(db.Model):
    """track std appn to pd"""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student_profiles.id'), nullable=False)
    drive_id = Column(Integer, ForeignKey('placement_drives.id'), nullable=False)
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='applied')  # all opt applied,shortlisted,test_invited,interview,selected,rejected
    feedback = Column(Text)
    test_link = Column(String(500), nullable=True)
    test_scheduled = Column(DateTime, nullable=True)
    interview_link = Column(String(500), nullable=True)
    interview_scheduled = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    # 1 appn for 1 std for 1 pd
    __table_args__ = (
        UniqueConstraint('student_id', 'drive_id', name='uq_student_drive'),
    )

    # only 1 placement if std selected
    placement = relationship('Placement', backref='application', uselist=False)

    def to_dict(self) -> dict: # give a dict in json has all std pd info
        student_name = None
        if self.student:
            student_name = self.student.full_name

        drive_title = None
        company_name = None
        if self.drive:
            drive_title = self.drive.job_title
            if self.drive.company:
                company_name = self.drive.company.company_name

        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': student_name,
            'drive_id': self.drive_id,
            'drive_title': drive_title,
            'company_name': company_name,
            'application_date': (
                self.application_date.isoformat() + 'Z' if self.application_date else None
            ),
            'status': self.status,
            'feedback': self.feedback,
            'test_link': self.test_link,
            'test_scheduled': (
                self.test_scheduled.isoformat() + 'Z' if self.test_scheduled else None
            ),
            'interview_link': self.interview_link,
            'interview_scheduled': (
                self.interview_scheduled.isoformat() + 'Z' if self.interview_scheduled else None
            ),
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }



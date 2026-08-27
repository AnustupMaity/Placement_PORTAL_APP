"""confirm pmt - selected std """

from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from extensions import db

class Placement(db.Model):
    """mark confirm pmt from appn."""

    __tablename__ = 'placements'

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False, unique=True)
    student_id = Column(Integer, ForeignKey('student_profiles.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('company_profiles.id'), nullable=False)
    position = Column(String(200))
    salary = Column(String(50))
    joining_date = Column(Date, nullable=True)
    joining_location = Column(String(200), nullable=True)
    offer_letter_path = Column(String(500), nullable=True)
    student_signature_path = Column(String(500), nullable=True)
    company_signature_path = Column(String(500), nullable=True)
    is_accepted = Column(db.Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict: #json dict
        student_name = None
        student_branch = None
        student_phone = None
        student_skills = None
        student_resume = None
        student_email = None
        company_name = None
        application_feedback = None

        if self.application:
            if self.application.student:
                student_name = self.application.student.full_name
                student_branch = self.application.student.branch
                student_phone = self.application.student.phone
                student_skills = self.application.student.skills
                student_resume = self.application.student.resume_path
                if self.application.student.user:
                    student_email = self.application.student.user.email
            if self.application.drive and self.application.drive.company:
                company_name = self.application.drive.company.company_name
            application_feedback = self.application.feedback

        return {
            'id': self.id,
            'application_id': self.application_id,
            'student_id': self.student_id,
            'student_name': student_name,
            'student_branch': student_branch,
            'student_phone': student_phone,
            'student_skills': student_skills,
            'student_resume': student_resume,
            'student_email': student_email,
            'company_id': self.company_id,
            'company_name': company_name,
            'position': self.position,
            'salary': self.salary,
            'joining_date': self.joining_date.isoformat() + 'Z' if self.joining_date else None,
            'joining_location': self.joining_location,
            'offer_letter_path': self.offer_letter_path,
            'student_signature_path': self.student_signature_path,
            'company_signature_path': self.company_signature_path,
            'is_accepted': self.is_accepted,
            'accepted_at': self.accepted_at.isoformat() + 'Z' if self.accepted_at else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'feedback': application_feedback,
        }



""" pd made by comp"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db


class PlacementDrive(db.Model):
    """ pd made by comp"""

    __tablename__ = 'placement_drives'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company_profiles.id'), nullable=False)
    job_title = Column(String(200), nullable=False)
    job_description = Column(Text)
    required_skills = Column(Text)
    salary = Column(String(50))
    location = Column(String(200))
    eligible_branches = Column(Text)  # json..branch... CSE,ECE...
    min_cgpa = Column(Float, default=0.0)
    eligible_year = Column(Integer)
    application_deadline = Column(DateTime)
    interview_date = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # pending, approved, closed
    created_at = Column(DateTime, default=datetime.utcnow)

    # many app per pd
    applications = relationship(
        'Application', backref='drive', cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict: #json  of pd all info of comp

        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'required_skills': self.required_skills,
            'salary': self.salary,
            'location': self.location,
            'eligible_branches': self.eligible_branches,
            'min_cgpa': self.min_cgpa,
            'eligible_year': self.eligible_year,
            'application_deadline': (
                self.application_deadline.isoformat() + 'Z' if self.application_deadline else None
            ),
            'interview_date': (
                self.interview_date.isoformat() + 'Z' if self.interview_date else None
            ),
            'status': self.status,
            'applicant_count': len(self.applications) if self.applications else 0,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }



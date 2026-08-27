"""std"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db


class StudentProfile(db.Model):#std site with std role


    __tablename__ = 'student_profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    full_name = Column(String(200), nullable=False)
    roll_number = Column(String(50), unique=True)
    branch = Column(String(100))
    year = Column(Integer)  # passout
    cgpa = Column(Float)
    skills = Column(Text)  # use ,, 
    projects = Column(Text, nullable=True) # JSON or text list of projects
    experience = Column(Text, nullable=True) # Internships/Work Exp
    resume_path = Column(String(500))
    signature_path = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    phone = Column(String(20))
    is_blacklisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 1 std many appn
    applications = relationship(
        'Application', backref='student', cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict:#json dict std info
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'roll_number': self.roll_number,
            'branch': self.branch,
            'year': self.year,
            'cgpa': self.cgpa,
            'skills': self.skills,
            'projects': self.projects,
            'experience': self.experience,
            'resume_path': self.resume_path,
            'signature_path': self.signature_path,
            'profile_image_url': self.profile_image_url,
            'phone': self.phone,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }



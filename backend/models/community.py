from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from extensions import db

class InterviewExperience(db.Model):
    __tablename__ = 'interview_experiences'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student_profiles.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('company_profiles.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False) # Rich text or markdown
    role = Column(String(100), nullable=True) # The job role
    is_anonymous = Column(Boolean, default=False)
    
    status = Column(String(20), default='approved') # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship('StudentProfile', backref='experiences')
    company = relationship('CompanyProfile', backref='experiences')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id if not self.is_anonymous else None,
            'student_name': self.student.full_name if not self.is_anonymous and self.student else 'Anonymous',
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'company_logo': self.company.logo_url if self.company else None,
            'title': self.title,
            'content': self.content,
            'role': self.role,
            'is_anonymous': self.is_anonymous,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }

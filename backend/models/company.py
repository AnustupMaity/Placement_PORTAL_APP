"""comp to user"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from extensions import db
class CompanyProfile(db.Model): # comp to particlar user 
    __tablename__ = 'company_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    website = Column(String(200))
    location = Column(String(200))
    description = Column(Text)
    hr_name = Column(String(100))
    hr_email = Column(String(120))
    hr_phone = Column(String(20))
    logo_url = Column(String(500))
    signature_path = Column(String(500), nullable=True)
    approval_status = Column(String(20), default='pending')  # pending , approved , rejected
    is_blacklisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # more than 1 pd per comp 
    drives = relationship(
        'PlacementDrive', backref='company', cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict: #give json dict all comp info
    
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'website': self.website,
            'location': self.location,
            'description': self.description,
            'hr_name': self.hr_name,
            'hr_email': self.hr_email,
            'hr_phone': self.hr_phone,
            'logo_url': self.logo_url,
            'signature_path': self.signature_path,
            'approval_status': self.approval_status,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }



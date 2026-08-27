"""user...auth + role """

from datetime import datetime
import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from extensions import db


class User(db.Model):#user auth for diff roles


    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False) 
    is_active = Column(Boolean, default=True)
    signature_path = Column(String(500), nullable=True)
    institute_name = Column(String(200), nullable=True)
    institute_logo_url = Column(String(500), nullable=True)
    institute_address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 1 user 1 role
    company_profile = relationship(
        'CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan'
    )
    student_profile = relationship(
        'StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan'
    )

    # for password 

    def set_password(self, password: str) -> None:#here using bcrypt py lib to protect password will be hashed form in db ,check hash match 
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8'),
        )



    def to_dict(self) -> dict:#json dict without password

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'signature_path': self.signature_path,
            'institute_name': self.institute_name,
            'institute_logo_url': self.institute_logo_url,
            'institute_address': self.institute_address,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }



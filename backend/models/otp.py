from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from extensions import db

class OTP(db.Model):
    __tablename__ = 'otps'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(db.Boolean, default=False)

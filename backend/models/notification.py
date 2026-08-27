from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from extensions import db

class Notification(db.Model):
    """Stores in-app notifications for users."""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True) # ID of the user (Admin, Company, or Student)
    user_type = Column(String(20), nullable=False) # 'admin', 'company', 'student'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True) # Optional link to direct the user
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }

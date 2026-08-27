from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class MessageThread(db.Model):
    """Represents a conversation thread or broadcast."""
    __tablename__ = 'message_threads'

    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Null if broadcast
    recipient_group = Column(String(50), nullable=True) # e.g., 'all_students', 'admin', 'drive_X'
    status = Column(String(20), default='open') # 'open', 'resolved'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship('User', foreign_keys=[creator_id], backref='created_threads')
    recipient = relationship('User', foreign_keys=[recipient_id], backref='received_threads')
    replies = relationship('MessageReply', backref='thread', cascade='all, delete-orphan', order_by='MessageReply.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'creator_id': self.creator_id,
            'creator_name': self.creator.username if self.creator else 'Unknown',
            'creator_role': self.creator.role if self.creator else 'Unknown',
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.username if self.recipient else None,
            'recipient_group': self.recipient_group,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'reply_count': len(self.replies)
        }

class MessageReply(db.Model):
    """Represents a single message within a thread."""
    __tablename__ = 'message_replies'

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('message_threads.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship('User', foreign_keys=[sender_id])

    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else 'Unknown',
            'sender_role': self.sender.role if self.sender else 'Unknown',
            'body': self.body,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }

from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_
from extensions import db, socketio
from models.user import User
from models.message import MessageThread, MessageReply
from models.notification import Notification
from utils.decorators import token_required

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/api/messages', methods=['GET'])
@token_required
def get_threads():
    user = g.current_user
    
    # Fetch threads where user is creator OR recipient OR it's a broadcast that applies to them
    # For simplicity, if recipient_group is set, we check if the user belongs to it
    
    query = MessageThread.query.filter(
        or_(
            MessageThread.creator_id == user.id,
            MessageThread.recipient_id == user.id,
            MessageThread.recipient_group == 'all',
            # Add specific group logic here if needed (e.g., 'all_students' if user.role == 'student')
            db.and_(MessageThread.recipient_group == 'all_students', user.role == 'student'),
            db.and_(MessageThread.recipient_group == 'all_companies', user.role == 'company'),
            db.and_(MessageThread.recipient_group == 'admin', user.role == 'admin')
        )
    ).order_by(MessageThread.created_at.desc())
    
    threads = query.all()
    return jsonify([t.to_dict() for t in threads]), 200

@messages_bp.route('/api/messages/<int:thread_id>', methods=['GET'])
@token_required
def get_thread_replies(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)
    
    # We should ensure the user has access to this thread
    user = g.current_user
    has_access = (
        thread.creator_id == user.id or 
        thread.recipient_id == user.id or 
        user.role == 'admin' or
        (thread.recipient_group == 'all') or
        (thread.recipient_group == 'all_students' and user.role == 'student') or
        (thread.recipient_group == 'all_companies' and user.role == 'company') or
        (thread.recipient_group == 'admin' and user.role == 'admin')
    )
    
    if not has_access:
        return jsonify({'error': 'Unauthorized'}), 403
        
    return jsonify({
        'thread': thread.to_dict(),
        'replies': [r.to_dict() for r in thread.replies]
    }), 200

@messages_bp.route('/api/messages', methods=['POST'])
@token_required
def create_thread():
    user = g.current_user
    data = request.get_json(silent=True) or {}
    
    subject = data.get('subject')
    body = data.get('body')
    recipient_id = data.get('recipient_id')
    recipient_group = data.get('recipient_group') # 'all_students', 'admin', etc.
    
    if not subject or not body:
        return jsonify({'error': 'Subject and body are required'}), 400
        
    if not recipient_id and not recipient_group:
        return jsonify({'error': 'Recipient is required'}), 400
        
    # Security: only admin/company can broadcast
    if recipient_group and recipient_group != 'admin' and user.role == 'student':
        return jsonify({'error': 'Students cannot broadcast messages'}), 403

    thread = MessageThread(
        subject=subject,
        creator_id=user.id,
        recipient_id=recipient_id,
        recipient_group=recipient_group
    )
    db.session.add(thread)
    db.session.flush() # get thread.id
    
    reply = MessageReply(
        thread_id=thread.id,
        sender_id=user.id,
        body=body
    )
    db.session.add(reply)
    
    # Notify specific recipient if applicable
    if recipient_id:
        notif = Notification(
            user_id=recipient_id,
            user_type=User.query.get(recipient_id).role,
            title="New Message Received",
            message=f"You received a new message regarding: {subject}",
            link="/messages"
        )
        db.session.add(notif)
        
    # Note: Broadcasting notifications can be heavy, we'll skip creating individual notifications for 'all' groups
    # Users will see it in their messages tab.
        
    db.session.commit()
    
    # Emit real-time event
    if recipient_id:
        socketio.emit('new_thread', thread.to_dict(), room=f'user_{recipient_id}')
    elif recipient_group:
        socketio.emit('new_thread', thread.to_dict(), room=f'group_{recipient_group}')
        
    return jsonify(thread.to_dict()), 201

@messages_bp.route('/api/messages/<int:thread_id>/reply', methods=['POST'])
@token_required
def reply_thread(thread_id):
    user = g.current_user
    thread = MessageThread.query.get_or_404(thread_id)
    
    if thread.status == 'resolved':
        return jsonify({'error': 'Cannot reply to a resolved thread'}), 400
        
    data = request.get_json(silent=True) or {}
    body = data.get('body')
    
    if not body:
        return jsonify({'error': 'Reply body is required'}), 400
        
    reply = MessageReply(
        thread_id=thread.id,
        sender_id=user.id,
        body=body
    )
    db.session.add(reply)
    
    # Notify the other party
    other_party_id = thread.creator_id if user.id != thread.creator_id else thread.recipient_id
    if other_party_id:
        notif = Notification(
            user_id=other_party_id,
            user_type=User.query.get(other_party_id).role,
            title="New Reply",
            message=f"New reply in thread: {thread.subject}",
            link="/messages"
        )
        db.session.add(notif)
        
    db.session.commit()
    
    # Emit real-time reply event
    socketio.emit('new_reply', reply.to_dict(), room=f'thread_{thread.id}')
    
    return jsonify(reply.to_dict()), 201

@messages_bp.route('/api/messages/<int:thread_id>/resolve', methods=['PUT'])
@token_required
def resolve_thread(thread_id):
    user = g.current_user
    thread = MessageThread.query.get_or_404(thread_id)
    
    # Allow creator or admin to resolve
    if thread.creator_id != user.id and user.role != 'admin' and thread.recipient_id != user.id:
        return jsonify({'error': 'Unauthorized to resolve this thread'}), 403
        
    thread.status = 'resolved'
    db.session.commit()
    
    return jsonify({'message': 'Thread marked as resolved'}), 200

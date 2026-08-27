from flask import Blueprint, jsonify, g
from extensions import db
from models.notification import Notification
from utils.decorators import token_required

notifications_bp = Blueprint('notifications', __name__)

def _get_user_info():
    user = g.current_user
    if user.role == 'admin':
        return user.id, 'admin'
    elif user.role == 'company':
        return user.id, 'company'
    elif user.role == 'student':
        return user.id, 'student'
    return None, None

@notifications_bp.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    user_id, user_type = _get_user_info()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notifications = Notification.query.filter_by(
        user_id=user_id, user_type=user_type
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return jsonify([n.to_dict() for n in notifications]), 200

@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    user_id, user_type = _get_user_info()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    count = Notification.query.filter_by(
        user_id=user_id, user_type=user_type, is_read=False
    ).count()

    return jsonify({'count': count}), 200

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_read(notification_id):
    user_id, user_type = _get_user_info()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notification = Notification.query.filter_by(
        id=notification_id, user_id=user_id, user_type=user_type
    ).first()

    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({'message': 'Marked as read'}), 200

@notifications_bp.route('/api/notifications/read-all', methods=['PUT'])
@token_required
def mark_all_read():
    user_id, user_type = _get_user_info()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    Notification.query.filter_by(
        user_id=user_id, user_type=user_type, is_read=False
    ).update({'is_read': True})
    db.session.commit()

    return jsonify({'message': 'All marked as read'}), 200

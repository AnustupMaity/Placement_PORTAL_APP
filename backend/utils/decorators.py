#auth+access

from functools import wraps

import jwt
from flask import request, jsonify, g, current_app

from extensions import db
from models.user import User

#llm help has been taken in this code file...partially

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'missing auth header.'}), 401
        token = auth_header.split(' ', 1)[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'invalid token'}), 401
        user = db.session.get(User, payload.get('user_id'))
        if user is None:
            return jsonify({'error': 'user not found'}), 401

        if not user.is_active:
            return jsonify({'error': 'deactivated'}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):#role decorater
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.current_user.role not in roles:
                return jsonify({
                    'error': 'access denied',
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

#py app.py

import os
import eventlet
eventlet.monkey_patch()
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, mail, init_redis, make_celery

def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder=None,#disable using backend/static as fronend in frontend folder
        template_folder='templates',  # backend/template/index.html
    )
    app.config.from_object(config_class)

    db.init_app(app)#sqlahmy connect flask
    mail.init_app(app)#flask maul connect
    init_redis(app)#redis connect
    
    from extensions import socketio, limiter, redis_client
    
    if redis_client is not None:
        redis_url = app.config.get('REDIS_URL')
        socketio.init_app(app, message_queue=redis_url)
    else:
        socketio.init_app(app)
        
    limiter.init_app(app)

    #here the code below... CORS was suggested by chatgpt to avoid future errors
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    #blueprint
    _register_blueprints(app)

    # seed db table + admin + migrations
    with app.app_context():#all model import
        import models
        import models.community
        import models.message
        import models.otp
        db.create_all()
        _migrate_db_columns()
        _seed_admin()
    _register_frontend_routes(app)#route frontend serve 
    _register_error_handlers(app)#global error handlers
    return app




def _register_blueprints(app):#blueprint all routes
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    try:
        from routes.upload import upload_bp
        app.register_blueprint(upload_bp)
    except ImportError:
        app.logger.info('upload bp missing')

    try:
        from routes.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        app.logger.info('admin bp missing')

    try:
        from routes.company import company_bp
        app.register_blueprint(company_bp)
    except ImportError:
        app.logger.info('company bp missing')

    try:
        from routes.student import student_bp
        app.register_blueprint(student_bp)
    except ImportError:
        app.logger.info('student bp missing')

    try:
        from routes.export import export_bp
        app.register_blueprint(export_bp)
    except ImportError:
        app.logger.info('export bp missing')

    try:
        from routes.notifications import notifications_bp
        app.register_blueprint(notifications_bp)
    except ImportError as e:
        app.logger.warning(f"Could not load notifications routes: {e}")

    try:
        from routes.community import community_bp
        app.register_blueprint(community_bp)
        app.logger.info("Registered community blueprint")
    except ImportError as e:
        app.logger.warning(f"Could not load community routes: {e}")

    try:
        from routes.messages import messages_bp
        app.register_blueprint(messages_bp)
        app.logger.info("Registered messages blueprint")
    except ImportError as e:
        app.logger.warning(f"Could not load messages routes: {e}")

    try:
        from routes.ai import ai_bp
        app.register_blueprint(ai_bp)
        app.logger.info("Registered ai blueprint")
    except ImportError as e:
        app.logger.warning(f"Could not load ai routes: {e}")


def _migrate_db_columns():
    """Ensure columns exist in existing tables (supports both SQLite and Postgres)."""
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(db.engine)
        
        def add_column_if_not_exists(table_name, column_name, column_type):
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if column_name not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                    conn.commit()

        if inspector.has_table('placements'):
            add_column_if_not_exists('placements', 'student_signature_path', 'VARCHAR(500)')
            add_column_if_not_exists('placements', 'company_signature_path', 'VARCHAR(500)')

        if inspector.has_table('company_profiles'):
            add_column_if_not_exists('company_profiles', 'signature_path', 'VARCHAR(500)')

        if inspector.has_table('student_profiles'):
            add_column_if_not_exists('student_profiles', 'signature_path', 'VARCHAR(500)')
            add_column_if_not_exists('student_profiles', 'projects', 'TEXT')
            add_column_if_not_exists('student_profiles', 'experience', 'TEXT')

        if inspector.has_table('users'):
            add_column_if_not_exists('users', 'institute_name', 'VARCHAR(200)')
            add_column_if_not_exists('users', 'institute_logo_url', 'VARCHAR(500)')
            add_column_if_not_exists('users', 'institute_address', 'VARCHAR(500)')
            add_column_if_not_exists('users', 'signature_path', 'VARCHAR(500)')

    except Exception as e:
        print(f"Migration note: {e}")


# seed admin
def _seed_admin():
    from models.user import User

    if User.query.filter_by(role='admin').first() is None:
        admin_user = os.environ.get('PPA_ADMIN_USER', 'admin')
        admin_email = os.environ.get('PPA_ADMIN_EMAIL', 'admin@ppa.com')
        admin_pass = os.environ.get('PPA_ADMIN_PASSWORD', 'admin123')
        
        admin = User(
            username=admin_user,
            email=admin_email,
            role='admin',
        )
        admin.set_password(admin_pass)
        db.session.add(admin)
        db.session.commit()
        print(f'Admin account seeded: {admin_user} / {admin_pass}')


# frontend route
def _register_frontend_routes(app):
    project_root = os.path.abspath(os.path.join(app.root_path, '..'))
    frontend_dir = os.path.join(project_root, 'frontend')

    @app.route('/')
    def serve_index():#index page
        from flask import render_template
        return render_template('index.html')

    @app.route('/frontend/<path:filepath>')
    def serve_frontend(filepath):#frontend other pages
        return send_from_directory(frontend_dir, filepath)

    @app.route('/manifest.json')#pwa behavior
    def serve_manifest():
        return send_from_directory(frontend_dir, 'manifest.json')

    @app.route('/sw.js') #pwa sw 
    def serve_sw():
        return send_from_directory(frontend_dir, 'sw.js')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_catch_all(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Not found.'}), 404
        from flask import render_template
        return render_template('index.html')


def _register_error_handlers(app):
    from flask import jsonify, request
    import traceback

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled Exception: {e}\n{traceback.format_exc()}')
        if hasattr(e, 'code'):
            return jsonify({'error': str(e)}), getattr(e, 'code', 500)
        return jsonify({'error': 'An unexpected internal server error occurred.'}), 500


def _register_socketio_events(socketio):
    from flask_socketio import join_room, leave_room
    
    @socketio.on('join')
    def on_join(data):
        # Extremely basic join handler for real-time rooms
        user_id = data.get('user_id')
        role = data.get('role')
        thread_id = data.get('thread_id')
        
        if user_id:
            join_room(f'user_{user_id}')
        if role == 'student':
            join_room('group_all_students')
        if role == 'company':
            join_room('group_all_companies')
        if role == 'admin':
            join_room('group_admin')
        if thread_id:
            join_room(f'thread_{thread_id}')
            
    @socketio.on('leave')
    def on_leave(data):
        thread_id = data.get('thread_id')
        if thread_id:
            leave_room(f'thread_{thread_id}')


app = create_app()
celery = make_celery(app)

if __name__ == '__main__':
    from extensions import socketio
    _register_socketio_events(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

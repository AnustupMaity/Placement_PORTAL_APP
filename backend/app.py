#py app.py

import os
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

    #here the code below... CORS was suggested by chatgpt to avoid future errors
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    #blueprint
    _register_blueprints(app)

    # seed db table + admin + migrations
    with app.app_context():#all model import
        import models
        import models.community
        import models.message
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


def _migrate_db_columns():
    """Ensure SQLite columns for signature support exist in existing tables."""
    from sqlalchemy import text
    try:
        # Check and add columns to placements
        with db.engine.connect() as conn:
            # placement columns
            res = conn.execute(text("PRAGMA table_info(placements)")).fetchall()
            existing_cols = [r[1] for r in res]
            if 'student_signature_path' not in existing_cols:
                conn.execute(text("ALTER TABLE placements ADD COLUMN student_signature_path VARCHAR(500)"))
            if 'company_signature_path' not in existing_cols:
                conn.execute(text("ALTER TABLE placements ADD COLUMN company_signature_path VARCHAR(500)"))

            # company_profiles columns
            res_comp = conn.execute(text("PRAGMA table_info(company_profiles)")).fetchall()
            existing_comp_cols = [r[1] for r in res_comp]
            if 'signature_path' not in existing_comp_cols:
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN signature_path VARCHAR(500)"))

            # student_profiles columns
            res_std = conn.execute(text("PRAGMA table_info(student_profiles)")).fetchall()
            existing_std_cols = [r[1] for r in res_std]
            if 'signature_path' not in existing_std_cols:
                conn.execute(text("ALTER TABLE student_profiles ADD COLUMN signature_path VARCHAR(500)"))

            # users columns
            res_usr = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            existing_usr_cols = [r[1] for r in res_usr]
            if 'institute_name' not in existing_usr_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN institute_name VARCHAR(200)"))
            if 'institute_logo_url' not in existing_usr_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN institute_logo_url VARCHAR(500)"))
            if 'institute_address' not in existing_usr_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN institute_address VARCHAR(500)"))

            conn.commit()
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

    @app.route('/<path:path>')#catch all - suggested by llm
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


app = create_app()
celery = make_celery(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#auth login+register+current login info

from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify, g, current_app
from extensions import db
from models.user import User
from models.company import CompanyProfile
from models.student import StudentProfile
from utils.decorators import token_required
from utils.validators import validate_email, validate_required, validate_cgpa

auth_bp = Blueprint('auth', __name__)


#REGISTER ROUTE

@auth_bp.route('/api/auth/register/student', methods=['POST'])#register std
def register_student():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
        
    ok, err = validate_required(data, ['username', 'email', 'password', 'full_name'])
    if not ok:
        return jsonify({'error': err}), 400

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    if not validate_email(email):
        return jsonify({'error': 'Invalid email address.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken.'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 409

    cgpa = data.get('cgpa')
    if cgpa is not None:
        valid, msg = validate_cgpa(cgpa)
        if not valid:
            return jsonify({'error': msg}), 400
        cgpa = float(cgpa)

    user = User(username=username, email=email, role='student')
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()

        profile = StudentProfile(
            user_id=user.id,
            full_name=data['full_name'].strip(),
            roll_number=data.get('roll_number', '').strip() or None,
            branch=data.get('branch', '').strip() or None,
            year=data.get('year'),
            cgpa=cgpa,
            phone=data.get('phone', '').strip() or None,
            resume_path=data.get('resume_path', '').strip() or None,
        )
        db.session.add(profile)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Student Registration error: {e}')
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

    token = _generate_token(user)#JWT..USED LLM HERE
    return jsonify({
        'message': 'Registration successful.',
        'token': token,
        'user': user.to_dict(),
    }), 201


@auth_bp.route('/api/auth/register/company', methods=['POST'])#register comp
def register_company():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
        
    ok, err = validate_required(data, ['username', 'email', 'password', 'company_name'])
    if not ok:
        return jsonify({'error': err}), 400

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    if not validate_email(email):
        return jsonify({'error': 'Invalid email address.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken.'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 409

    user = User(username=username, email=email, role='company')
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()

        profile = CompanyProfile(
            user_id=user.id,
            company_name=data['company_name'].strip(),
            industry=data.get('industry', '').strip() or None,
            website=data.get('website', '').strip() or None,
            location=data.get('location', '').strip() or None,
            description=data.get('description', '').strip() or None,
            hr_name=data.get('hr_name', '').strip() or None,
            hr_email=data.get('hr_email', '').strip() or None,
            hr_phone=data.get('hr_phone', '').strip() or None,
            approval_status='pending',
        )
        db.session.add(profile)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Company Registration error: {e}')
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

    return jsonify({
        'message': 'Registration successful. Please wait for admin approval before logging in.',
        'user': user.to_dict(),
        'approval_status': 'pending'
    }), 201


#LOGIN ROUTE

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    identifier = data.get('username', '').strip() or data.get('email', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Username/email and password are required.'}), 400

    user = User.query.filter(
        (User.username.ilike(identifier)) | (User.email == identifier.lower())
    ).first()

    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    if user.role == 'company' and user.company_profile:
        status = user.company_profile.approval_status
        if status == 'pending':
            return jsonify({'error': 'Your company account is pending admin approval. Please wait.'}), 403
        elif status == 'rejected':
            return jsonify({'error': 'Your company account registration was rejected by the admin.'}), 403

    token = _generate_token(user)#JWT..USED LLM HERE

    response = {
        'message': 'Login successful.',
        'token': token,
        'user': user.to_dict(),
    }

    if user.role == 'company' and user.company_profile:#comp need admin aprove
        response['approval_status'] = user.company_profile.approval_status

    return jsonify(response), 200


@auth_bp.route('/api/auth/google', methods=['POST'])
def google_login():
    """
    Authenticate or Register via Google OAuth / Google Identity Services.
    Accepts credential (JWT) or direct Google user details.
    """
    data = request.get_json(silent=True) or {}
    credential = data.get('credential')
    email = None
    name = None
    google_id = None
    picture = None

    if credential:
        try:
            # Decode Google JWT payload safely
            decoded = jwt.decode(credential, options={"verify_signature": False})
            email = decoded.get('email', '').strip().lower()
            name = decoded.get('name', '').strip()
            google_id = decoded.get('sub')
            picture = decoded.get('picture')
        except Exception as e:
            return jsonify({'error': f'Invalid Google credential token: {str(e)}'}), 400
    else:
        email = (data.get('email') or '').strip().lower()
        name = (data.get('name') or '').strip()
        google_id = data.get('google_id') or data.get('sub')
        picture = data.get('picture')

    if not email:
        return jsonify({'error': 'No valid Google email found in request.'}), 400

    target_role = data.get('role', 'student')
    if target_role not in ['student', 'company']:
        target_role = 'student'

    user = User.query.filter_by(email=email).first()

    # If user doesn't exist, register them automatically
    if not user:
        # Generate clean unique username
        base_username = email.split('@')[0].replace('.', '_').replace('-', '_')
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first() is not None:
            username = f"{base_username}_{counter}"
            counter += 1

        import secrets
        random_password = secrets.token_hex(16)

        user = User(
            username=username,
            email=email,
            role=target_role,
        )
        user.set_password(random_password)

        try:
            db.session.add(user)
            db.session.flush()

            if target_role == 'student':
                profile = StudentProfile(
                    user_id=user.id,
                    full_name=name or username.capitalize(),
                )
                db.session.add(profile)
            elif target_role == 'company':
                profile = CompanyProfile(
                    user_id=user.id,
                    company_name=name or username.capitalize(),
                    approval_status='pending',
                )
                db.session.add(profile)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to create account: {str(e)}'}), 500

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact administrator.'}), 403

    if user.role == 'company' and user.company_profile:
        if user.company_profile.approval_status == 'pending':
            return jsonify({'error': 'Your company account is pending admin approval.'}), 403
        elif user.company_profile.approval_status == 'rejected':
            return jsonify({'error': 'Your company account was rejected by admin.'}), 403

    token = _generate_token(user)

    return jsonify({
        'message': 'Google Login successful.',
        'token': token,
        'user': user.to_dict(),
        'is_new_user': not bool(user.created_at and (datetime.utcnow() - user.created_at).total_seconds() > 10)
    }), 200


@auth_bp.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    """Return relevant dynamic notifications for the current authenticated user."""
    user = g.current_user
    notifications = []

    try:
        from models.drive import PlacementDrive
        from models.application import Application
        from models.placement import Placement
        from models.company import CompanyProfile

        if user.role == 'student' and user.student_profile:
            # 1. Offers waiting for student signature / acceptance
            pending_placements = Placement.query.filter_by(student_id=user.student_profile.id, is_accepted=False).all()
            for p in pending_placements:
                notifications.append({
                    'id': f'offer-{p.id}',
                    'title': 'Job Offer Received!',
                    'message': f'You have an offer for {p.position} at {p.company.company_name if p.company else "Company"}. Please sign to accept.',
                    'link': '/student/history',
                    'type': 'offer',
                    'time': p.created_at.isoformat() + 'Z' if p.created_at else None,
                    'unread': True
                })

            # 2. Status changes on applications
            apps = Application.query.filter_by(student_id=user.student_profile.id).order_by(Application.application_date.desc()).limit(5).all()
            for a in apps:
                if a.status in ['shortlisted', 'interview']:
                    notifications.append({
                        'id': f'app-{a.id}',
                        'title': f'Application {a.status.capitalize()}!',
                        'message': f'Your application for {a.drive.job_title if a.drive else "Role"} has been marked as {a.status}.',
                        'link': '/student/applications',
                        'type': 'status',
                        'time': a.application_date.isoformat() + 'Z' if a.application_date else None,
                        'unread': False
                    })

            # 3. New approved drives
            recent_drives = PlacementDrive.query.filter_by(status='approved').order_by(PlacementDrive.created_at.desc()).limit(3).all()
            for d in recent_drives:
                notifications.append({
                    'id': f'drive-{d.id}',
                    'title': 'New Drive Posted',
                    'message': f'{d.company.company_name if d.company else "Company"} is hiring for {d.job_title} ({d.salary or "Package"}).',
                    'link': f'/student/drives/{d.id}',
                    'type': 'drive',
                    'time': d.created_at.isoformat() + 'Z' if d.created_at else None,
                    'unread': False
                })

        elif user.role == 'company' and user.company_profile:
            # New applicants
            comp_id = user.company_profile.id
            recent_apps = (
                db.session.query(Application)
                .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
                .filter(PlacementDrive.company_id == comp_id)
                .order_by(Application.application_date.desc())
                .limit(5)
                .all()
            )
            for a in recent_apps:
                notifications.append({
                    'id': f'capp-{a.id}',
                    'title': 'New Applicant',
                    'message': f'{a.student.full_name if a.student else "Candidate"} applied for {a.drive.job_title if a.drive else "Drive"}.',
                    'link': '/company/applications',
                    'type': 'applicant',
                    'time': a.application_date.isoformat() + 'Z' if a.application_date else None,
                    'unread': a.status == 'applied'
                })

        elif user.role == 'admin':
            # Pending companies
            pending_comps = CompanyProfile.query.filter_by(approval_status='pending').all()
            for c in pending_comps:
                notifications.append({
                    'id': f'pcomp-{c.id}',
                    'title': 'Pending Company Approval',
                    'message': f'{c.company_name} is awaiting administrative review.',
                    'link': '/admin/companies',
                    'type': 'company',
                    'time': c.created_at.isoformat() + 'Z' if c.created_at else None,
                    'unread': True
                })

    except Exception as e:
        current_app.logger.error(f"Error fetching notifications: {e}")

    return jsonify({'notifications': notifications, 'unread_count': sum(1 for n in notifications if n.get('unread'))}), 200


@auth_bp.route('/api/auth/me', methods=['GET'])#user prof info view except admin
@token_required
def me():
    user = g.current_user
    data = user.to_dict()

    if user.role == 'student' and user.student_profile:
        data['profile'] = user.student_profile.to_dict()
    elif user.role == 'company' and user.company_profile:
        data['profile'] = user.company_profile.to_dict()
    elif user.role == 'admin':
        data['profile'] = None #no profile

    return jsonify(data), 200



def _generate_token(user: User) -> str:#helper func #hlp of llm taken for jwt usage
    payload = {
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24),#24 hr valid
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')#secret key in config.py

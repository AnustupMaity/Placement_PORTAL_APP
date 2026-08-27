#company route token+role needed

from datetime import datetime
import json
from flask import Blueprint, request, jsonify, g
from sqlalchemy import func
from extensions import db
from models.user import User
from models.company import CompanyProfile
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.application import Application
from models.placement import Placement
from utils.decorators import token_required, role_required
from utils.cache import cache_get, cache_set, cache_delete, cache_delete_pattern
company_bp = Blueprint('company', __name__)

def _get_company_profile():#helper func to get specific company after auth
    return CompanyProfile.query.filter_by(user_id=g.current_user.id).first()

@company_bp.route('/api/company/dashboard', methods=['GET'])#dashboard comp wise
@token_required
@role_required('company')
def dashboard():#comp dash
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    if company.approval_status != 'approved':
        return jsonify({'error': 'not approved yet'}), 403
    #comp dash stats
    total_drives = PlacementDrive.query.filter_by(company_id=company.id).count()
    active_drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').count()
    pending_drives = PlacementDrive.query.filter_by(company_id=company.id, status='pending').count()

    #count of appn
    total_applications = (
        db.session.query(func.count(Application.id))
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
        .scalar()
    )

    total_placements = Placement.query.filter_by(company_id=company.id).count()

    return jsonify({
        'company': {
            'id': company.id,
            'company_name': company.company_name,
            'approval_status': company.approval_status,
            'is_blacklisted': company.is_blacklisted,
        },
        'total_drives': total_drives,
        'active_drives': active_drives,
        'pending_drives': pending_drives,
        'total_applications': total_applications or 0,
        'total_placements': total_placements,
    }), 200


@company_bp.route('/api/company/profile', methods=['GET'])#comp profile after auth
@token_required
@role_required('company')
def get_profile():
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    return jsonify({
        'id': company.id,
        'user_id': company.user_id,
        'company_name': company.company_name,
        'industry': company.industry,
        'website': company.website,
        'location': company.location,
        'description': company.description,
        'hr_name': company.hr_name,
        'hr_email': company.hr_email,
        'hr_phone': company.hr_phone,
        'logo_url': company.logo_url,
        'signature_path': company.signature_path,
        'approval_status': company.approval_status,
        'is_blacklisted': company.is_blacklisted,
        'created_at': company.created_at.isoformat() + 'Z' if company.created_at else None,
    }), 200


@company_bp.route('/api/company/profile', methods=['PUT'])#edit comp data
@token_required
@role_required('company')
def update_profile():
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.get_json(silent=True) or {}

    updatable_fields = [
        'company_name', 'industry', 'website', 'location',
        'description', 'hr_name', 'hr_email', 'hr_phone',
        'logo_url', 'signature_path', 'offer_template'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200


#comp site drive page....create drive 
@company_bp.route('/api/company/drives', methods=['POST'])
@token_required
@role_required('company')
def create_drive():#create drive by approved comp
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    if company.approval_status != 'approved':
        return jsonify({'error': 'Company is not approved'}), 403

    if company.is_blacklisted:
        return jsonify({'error': 'Company is blacklisted'}), 403

    data = request.get_json(silent=True) or {}

    required_fields = ['job_title', 'job_description', 'application_deadline', 'location', 'salary']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:    #deadline 
        application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return jsonify({'error': 'invalid application_deadline'}), 400

    interview_date = None#interview date
    if data.get('interview_date'):
        try:
            interview_date = datetime.fromisoformat(data['interview_date'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({'error': 'invalid date'}), 400

    eligible_branches = data.get('eligible_branches', [])
    if isinstance(eligible_branches, list):
        normalized_branches = [str(b).strip().upper() for b in eligible_branches]#case format
        normalized_branches = list(set(normalized_branches))#remove duplicte
        eligible_branches = json.dumps(normalized_branches)
    else:
        eligible_branches = json.dumps([])

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data['job_description'],
        required_skills=data.get('required_skills'),
        salary=data['salary'],
        location=data['location'],
        eligible_branches=eligible_branches,
        min_cgpa=data.get('min_cgpa'),
        eligible_year=data.get('eligible_year'),
        application_deadline=application_deadline,
        interview_date=interview_date,
        status='approved',
    )

    db.session.add(drive)
    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')#delete all info abt that drive pattern

    return jsonify({
        'message': 'Placement drive created ',
        'drive_id': drive.id,
    }), 201


@company_bp.route('/api/company/drives', methods=['GET'])#show drive list on the comp site drive page
@token_required
@role_required('company')
def list_drives():
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    status = request.args.get('status', '').strip()

    query = PlacementDrive.query.filter_by(company_id=company.id)
    if status:
        query = query.filter_by(status=status)

    drives = query.order_by(PlacementDrive.created_at.desc()).all()

    result = []
    for drive in drives:
        apps = Application.query.filter_by(drive_id=drive.id).all()
        stats = {
            'total': len(apps),
            'applied': sum(1 for a in apps if a.status == 'applied'),
            'shortlisted': sum(1 for a in apps if a.status == 'shortlisted'),
            'interview': sum(1 for a in apps if a.status == 'interview'),
            'selected': sum(1 for a in apps if a.status == 'selected'),
            'rejected': sum(1 for a in apps if a.status == 'rejected'),
        }

        result.append({
            'id': drive.id,
            'job_title': drive.job_title,
            'job_description': drive.job_description,
            'required_skills': drive.required_skills,
            'salary': drive.salary,
            'location': drive.location,
            'eligible_branches': drive.eligible_branches,
            'min_cgpa': float(drive.min_cgpa) if drive.min_cgpa is not None else None,
            'eligible_year': drive.eligible_year,
            'application_deadline': drive.application_deadline.isoformat() + 'Z' if drive.application_deadline else None,
            'interview_date': drive.interview_date.isoformat() + 'Z' if drive.interview_date else None,
            'status': drive.status,
            'stats': stats,
            'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
        })

    return jsonify(result), 200


@company_bp.route('/api/company/drives/<int:id>', methods=['GET'])#particular drive info
@token_required
@role_required('company')
def get_drive(id):
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = PlacementDrive.query.filter_by(id=id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404

    applications_count = Application.query.filter_by(drive_id=drive.id).count()

    return jsonify({
        'id': drive.id,
        'company_id': drive.company_id,
        'job_title': drive.job_title,
        'job_description': drive.job_description,
        'required_skills': drive.required_skills,
        'salary': drive.salary,
        'location': drive.location,
        'eligible_branches': drive.eligible_branches,
        'min_cgpa': float(drive.min_cgpa) if drive.min_cgpa is not None else None,
        'eligible_year': drive.eligible_year,
        'application_deadline': drive.application_deadline.isoformat() + 'Z' if drive.application_deadline else None,
        'interview_date': drive.interview_date.isoformat() + 'Z' if drive.interview_date else None,
        'status': drive.status,
        'applications_count': applications_count,
        'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
    }), 200


@company_bp.route('/api/company/drives/<int:drive_id>/applications', methods=['GET'])
@token_required
@role_required('company')
def list_drive_applications(drive_id):#appn of drive placemnt
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found or does not belong to your company'}), 404

    applications = (
        db.session.query(Application, StudentProfile)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .filter(Application.drive_id == drive_id)
        .all()
    )

    result = []
    for app, student in applications:
        result.append({
            'id': app.id,
            'student_id': student.id,
            'full_name': student.full_name,
            'drive_title': drive.job_title,
            'branch': student.branch,
            'year': student.year,
            'cgpa': float(student.cgpa) if student.cgpa is not None else None,
            'skills': student.skills,
            'phone': student.phone,
            'resume_path': student.resume_path,
            'status': app.status,
            'feedback': app.feedback,
            'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'interview_scheduled': app.interview_scheduled.isoformat() + 'Z' if app.interview_scheduled else None,
        })

    return jsonify(result), 200

@company_bp.route('/api/company/applications', methods=['GET'])
@token_required
@role_required('company')
def list_all_applications():
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    applications = (
        db.session.query(Application, StudentProfile, PlacementDrive)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    result = []
    for app, student, drive in applications:
        result.append({
            'id': app.id,
            'student_id': student.id,
            'drive_id': drive.id,
            'drive_title': drive.job_title,
            'full_name': student.full_name,
            'branch': student.branch,
            'year': student.year,
            'cgpa': float(student.cgpa) if student.cgpa is not None else None,
            'skills': student.skills,
            'phone': student.phone,
            'resume_path': student.resume_path,
            'status': app.status,
            'feedback': app.feedback,
            'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'interview_scheduled': app.interview_scheduled.isoformat() + 'Z' if app.interview_scheduled else None,
        })

    return jsonify(result), 200


@company_bp.route('/api/company/drives/<int:id>/close', methods=['PUT'])
@token_required
@role_required('company')#close placmt drive
def close_drive(id):
    """Close a placement drive."""
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = PlacementDrive.query.filter_by(id=id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found or does not belong to your company'}), 404

    drive.status = 'closed'
    db.session.commit()

    cache_delete_pattern('drives:*')

    return jsonify({'message': 'Drive closed successfully'}), 200



@company_bp.route('/api/company/applications/<int:id>/status', methods=['PUT'])#comp site appn page 
@token_required
@role_required('company')
def update_application_status(id):#plmt drive-- studnt appn ..reject select interview shortlist

    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    application = Application.query.get(id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    # check appn ..is of drive of comp....check was suugested by chatgpt to add eblow code block
    drive = PlacementDrive.query.filter_by(
        id=application.drive_id, company_id=company.id
    ).first()
    if not drive:
        return jsonify({'error': 'Application does not belong to your company\'s drive'}), 403

    data = request.get_json(silent=True) or {}

    if application.status in ['selected', 'rejected']:
        return jsonify({'error': f'Application is already {application.status} and cannot be changed.'}), 400

    new_status = data.get('status')
    valid_statuses = ['shortlisted', 'test_invited', 'interview', 'selected', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({
            'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
        }), 400

    application.status = new_status#check new status after new

    if data.get('feedback'):
        application.feedback = data['feedback']

    if new_status == 'interview':
        interview_date_str = data.get('interview_scheduled')
        if interview_date_str:
            try:
                application.interview_scheduled = datetime.fromisoformat(interview_date_str.replace('Z', '+00:00'))
            except ValueError:
                pass
        application.interview_link = data.get('interview_link')
        
        # Trigger email if task exists
        from tasks.emails import send_interview_invite_email
        if application.interview_scheduled:
            date_formatted = application.interview_scheduled.strftime('%B %d, %Y at %I:%M %p')
            send_interview_invite_email.delay(
                application.id, 
                application.interview_link or "Will be shared separately", 
                date_formatted, 
                data.get('custom_message', '')
            )
            
    if new_status == 'test_invited':
        test_date_str = data.get('test_scheduled')
        if test_date_str:
            try:
                application.test_scheduled = datetime.fromisoformat(test_date_str.replace('Z', '+00:00'))
            except ValueError:
                pass
        application.test_link = data.get('test_link')
        
        from tasks.emails import send_test_link_email
        send_test_link_email.delay(
            application.id,
            application.test_link or "Will be shared separately",
            data.get('custom_message', '')
        )

    #if studnt selected...make plmt record 
    if new_status == 'selected':
        existing_placement = Placement.query.filter_by(
            application_id=application.id,
        ).first()

        company_sig = data.get('company_signature_path') or company.signature_path

        if not existing_placement:
            placement = Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=company.id,
                position=drive.job_title,
                salary=drive.salary,
                company_signature_path=company_sig,
            )
            db.session.add(placement)
        elif company_sig and not existing_placement.company_signature_path:
            existing_placement.company_signature_path = company_sig

    db.session.commit()

    # Invalidate caches
    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')
    cache_delete_pattern('students:*')

    return jsonify({'message': f'Application status updated to {new_status}'}), 200

@company_bp.route('/api/company/applications/bulk-status', methods=['PUT'])
@token_required
@role_required('company')
def bulk_update_status():
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.get_json(silent=True) or {}
    app_ids = data.get('application_ids', [])
    new_status = data.get('status')

    valid_statuses = ['shortlisted', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

    if not app_ids:
        return jsonify({'error': 'No applications selected.'}), 400

    apps = Application.query.filter(Application.id.in_(app_ids)).all()
    updated_count = 0
    drive_id = None
    
    for app in apps:
        if app.drive.company_id == company.id and app.status not in ['selected', 'rejected']:
            app.status = new_status
            updated_count += 1
            if not drive_id:
                drive_id = app.drive_id

    db.session.commit()
    
    # Invalidate caches
    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')
    
    # If shortlisted, optionally notify admin
    if new_status == 'shortlisted' and data.get('notify_admin') and drive_id:
        from tasks.emails import send_shortlist_to_admin_email
        send_shortlist_to_admin_email.delay(drive_id, company.company_name)

    return jsonify({'message': f'Successfully updated {updated_count} applications.'}), 200

#plmt record for comp

@company_bp.route('/api/company/placements', methods=['GET'])
@token_required
@role_required('company')
def list_placements():#plmt visible to comp
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    placements = Placement.query.filter_by(company_id=company.id).order_by(Placement.created_at.desc()).all()
    result = [p.to_dict() for p in placements]
    return jsonify(result), 200


@company_bp.route('/api/company/placements/<int:placement_id>/signature', methods=['PUT'])
@token_required
@role_required('company')
def update_placement_signature(placement_id):
    """Optionally update or attach company signature to a specific placement."""
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    placement = Placement.query.filter_by(id=placement_id, company_id=company.id).first()
    if not placement:
        return jsonify({'error': 'Placement not found'}), 404

    data = request.get_json(silent=True) or {}
    sig = data.get('company_signature_path') or company.signature_path
    placement.company_signature_path = sig
    db.session.commit()

    return jsonify({'message': 'Company signature updated on placement offer.', 'placement': placement.to_dict()}), 200



@company_bp.route('/api/company/analytics', methods=['GET'])#comp analytic page
@token_required
@role_required('company')
def company_analytics():#stats ...refesh 60 sec cache
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    cache_key = f'company:analytics:{company.id}'
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from sqlalchemy import func

    apps_by_status = (#appn status of comp drive
        db.session.query(Application.status, func.count(Application.id))
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
        .group_by(Application.status)
        .all()
    )
    app_stats = {status: count for status, count in apps_by_status}

    data = {
        'applications': app_stats
    }

    cache_set(cache_key, data, expiry=60)#cache setter
    return jsonify(data), 200

@company_bp.route('/api/company/students/<int:student_id>/applications', methods=['GET'])
@token_required
@role_required('company')
def get_student_applications(student_id):
    company = _get_company_profile()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    applications = (
        db.session.query(Application, PlacementDrive, Placement)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .outerjoin(Placement, Application.id == Placement.application_id)
        .filter(Application.student_id == student_id, PlacementDrive.company_id == company.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    result = []
    for app, drive, placement in applications:
        status_date = None
        if app.status == 'selected' and placement and placement.created_at:
            status_date = placement.created_at.isoformat() + 'Z'
        elif app.status == 'interview' and app.interview_scheduled:
            status_date = app.interview_scheduled.isoformat() + 'Z'

        student_acceptance = None
        if placement:
            student_acceptance = 'Accepted' if placement.is_accepted else 'Pending'

        result.append({
            'id': app.id,
            'drive_id': drive.id,
            'drive_title': drive.job_title,
            'status': app.status,
            'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'status_date': status_date,
            'student_acceptance': student_acceptance
        })

    return jsonify(result), 200

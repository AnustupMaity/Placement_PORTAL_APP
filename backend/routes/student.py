#std routes 
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import or_
from extensions import db
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.company import CompanyProfile
from models.application import Application
from models.placement import Placement
from utils.decorators import token_required, role_required
from utils.cache import cache_get, cache_set, cache_delete, cache_delete_pattern

student_bp = Blueprint('student', __name__)

def _get_student_profile():#helper func to get auth student prof
    return StudentProfile.query.filter_by(user_id=g.current_user.id).first()

@student_bp.route('/api/student/companies', methods=['GET'])#std companies page
@token_required
@role_required('student')
def student_list_companies():
    from sqlalchemy import func
    now = datetime.utcnow()
    search = request.args.get('search', '').strip()

    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile required'}), 403

    apps = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = {a.drive_id for a in apps}


    query = CompanyProfile.query.filter_by(approval_status='approved', is_blacklisted=False)
    if search:
        query = query.filter(CompanyProfile.company_name.ilike(f'%{search}%'))

    companies = query.all()
    result = []
    for company in companies:
        company_drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        total_drives = len(company_drives)
        
        active_drives_count = sum(1 for d in company_drives if d.status == 'approved' and d.application_deadline >= now)
        not_applied_count = sum(1 for d in company_drives if d.status == 'approved' and d.application_deadline >= now and d.id not in applied_drive_ids)
        applied_count = sum(1 for d in company_drives if d.id in applied_drive_ids)
        
        result.append({
            'id': company.id,
            'company_name': company.company_name,
            'industry': company.industry,
            'location': company.location,
            'website': company.website,
            'description': company.description,
            'active_drives': active_drives_count,
            'total_drives': total_drives,
            'not_applied_drives': not_applied_count,
            'applied_drives': applied_count,
        })
    return jsonify(result), 200


@student_bp.route('/api/student/companies/<int:company_id>/drives', methods=['GET'])#drives by company for students
@token_required
@role_required('student')
def student_company_drives(company_id):
    student = _get_student_profile()
    company = CompanyProfile.query.get_or_404(company_id)

    applied_drive_ids = set()
    if student:
        apps = Application.query.filter_by(student_id=student.id).all()
        applied_drive_ids = {a.drive_id for a in apps}

    drives = PlacementDrive.query.filter_by(company_id=company_id).filter(
        PlacementDrive.status.in_(['approved', 'closed', 'cancelled'])
    ).all()
    result = []
    now = datetime.utcnow()
    for d in drives:
        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'location': d.location,
            'salary': d.salary,
            'application_deadline': d.application_deadline.isoformat() + 'Z' if d.application_deadline else None,
            'interview_date': d.interview_date.isoformat() + 'Z' if d.interview_date else None,
            'min_cgpa': float(d.min_cgpa) if d.min_cgpa else None,
            'eligible_branches': d.eligible_branches,
            'eligible_year': d.eligible_year,
            'status': d.status,
            'is_open': d.application_deadline >= now if d.application_deadline else False,
            'applied': d.id in applied_drive_ids,
        })
    return jsonify({
        'company': {
            'id': company.id,
            'company_name': company.company_name,
            'industry': company.industry,
            'location': company.location,
            'website': company.website,
            'description': company.description,
        },
        'drives': result
    }), 200


@student_bp.route('/api/student/dashboard', methods=['GET'])#std dashboard after auth
@token_required
@role_required('student')
def dashboard():
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    total_applications = Application.query.filter_by(student_id=student.id).count()
    shortlisted_count = Application.query.filter_by(student_id=student.id, status='shortlisted').count()
    selected_count = Application.query.filter_by(student_id=student.id, status='selected').count()
    pending_count = Application.query.filter_by(student_id=student.id, status='applied').count()

    now = datetime.utcnow()
    active_drives_query = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline >= now
    )
    active_drives_count = active_drives_query.count()
    
    not_applied_count = active_drives_query.filter(
        ~PlacementDrive.id.in_(
            db.session.query(Application.drive_id).filter_by(student_id=student.id)
        )
    ).count()

    return jsonify({
        'student': {
            'id': student.id,
            'full_name': student.full_name,
            'branch': student.branch,
            'year': student.year,
            'cgpa': float(student.cgpa) if student.cgpa is not None else None,
            'is_blacklisted': student.is_blacklisted,
        },
        'total_applications': total_applications,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
        'pending_count': pending_count,
        'active_drives_count': active_drives_count,
        'not_applied_count': not_applied_count
    }), 200



@student_bp.route('/api/student/profile', methods=['GET'])#specific auth std profile in dash
@token_required
@role_required('student')
def get_profile():
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    return jsonify({
        'id': student.id,
        'user_id': student.user_id,
        'email': student.user.email,
        'full_name': student.full_name,
        'roll_number': student.roll_number,
        'branch': student.branch,
        'year': student.year,
        'cgpa': float(student.cgpa) if student.cgpa is not None else None,
        'skills': student.skills,
        'phone': student.phone,
        'resume_path': student.resume_path,
        'signature_path': student.signature_path,
        'is_blacklisted': student.is_blacklisted,
        'created_at': student.created_at.isoformat() + 'Z' if student.created_at else None,
    }), 200


@student_bp.route('/api/student/profile', methods=['PUT'])#edit std info
@token_required
@role_required('student')
def update_profile():
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    data = request.get_json(silent=True) or {}

    new_email = data.get('email', '').strip().lower()#emial update
    if new_email and new_email != student.user.email:
        from models.user import User
        if User.query.filter_by(email=new_email).first():
            return jsonify({'error': 'Email address is already in use by another account'}), 400
        student.user.email = new_email

    updatable_fields = ['full_name', 'roll_number', 'branch', 'year', 'cgpa', 'skills', 'phone', 'resume_path', 'signature_path', 'profile_image_url']

    for field in updatable_fields:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()

    cache_delete_pattern('students:*')

    return jsonify({'message': 'Profile updated successfully'}), 200



@student_bp.route('/api/student/drives', methods=['GET'])#std site drive page
@token_required
@role_required('student')
def list_drives():#show all plmt drive to std 5min sec cache
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()
    min_salary = request.args.get('min_salary', type=float)

    # used a cache key for plmt drive
    cache_key = f"drives:approved:{search}:{branch}:{min_salary}"
    # Note: cache disabled so closed/cancelled drives always show
    # cached = cache_get(cache_key)
    # if cached is not None:
    #     return jsonify(cached), 200

    now = datetime.utcnow()

    query = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
        .filter(PlacementDrive.status.in_(['approved', 'closed', 'cancelled']))
    )

    if search:
        pattern = f'%{search}%'
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(pattern),
                CompanyProfile.company_name.ilike(pattern),
            )
        )

    if branch:
        query = query.filter(PlacementDrive.eligible_branches.ilike(f'%{branch}%'))#json brach

    if min_salary is not None:
        query = query.filter(PlacementDrive.salary.isnot(None))#str salary 

    results = query.order_by(PlacementDrive.application_deadline.asc()).all()

    student = _get_student_profile()#drive id for applied
    applied_drive_ids = set()
    if student:
        applied_apps = Application.query.filter_by(student_id=student.id).all()
        applied_drive_ids = {app.drive_id for app in applied_apps}

    drives = []
    for drive, company in results:
        drives.append({
            'id': drive.id,
            'company_id': company.id,
            'company_name': company.company_name,
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
            'applied': drive.id in applied_drive_ids,
            'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
        })

    return jsonify(drives), 200


@student_bp.route('/api/student/drives/<int:id>', methods=['GET'])#show plmt drive detail
@token_required
@role_required('student')
def get_drive(id):
    drive = PlacementDrive.query.filter_by(id=id).first()
    if not drive or drive.status not in ['approved', 'closed', 'cancelled']:
        return jsonify({'error': 'Drive not found or not accessible'}), 404

    company = CompanyProfile.query.get(drive.company_id)

    student = StudentProfile.query.filter_by(user_id=g.current_user.id).first()#check if applied
    already_applied = False
    if student:
        existing = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        already_applied = existing is not None

    return jsonify({
        'id': drive.id,
        'company_id': drive.company_id,
        'company_name': company.company_name if company else None,
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
        'applied': already_applied,
        'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
    }), 200


@student_bp.route('/api/student/applications', methods=['POST'])#std site appn page ..appn fillup
@token_required
@role_required('student')
def apply_for_drive():#apply plmt drive for approve drive with deadline rem studnt not appliead and blacklist
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if student.is_blacklisted:#not blacklist
        return jsonify({'error': 'You are blacklisted and cannot apply for drives'}), 400

    data = request.get_json(silent=True) or {}
    drive_id = data.get('drive_id')

    if not drive_id:
        return jsonify({'error': 'drive_id is required'}), 400

    drive = PlacementDrive.query.get(drive_id)#if drive aproved
    if not drive:
        return jsonify({'error': 'Drive not found'}), 400

    if drive.status != 'approved':
        return jsonify({'error': 'This drive is not currently accepting applications'}), 400

    now = datetime.utcnow()#not pass deadline
    if drive.application_deadline and drive.application_deadline < now:
        return jsonify({'error': 'Application deadline has passed'}), 400

    existing = Application.query.filter_by(#not alreaady applied
        student_id=student.id, drive_id=drive_id
    ).first()
    if existing:
        return jsonify({'error': 'You have already applied for this drive'}), 400

    if drive.eligible_branches:#branch eligible check
        import json
        try:
            eligible = json.loads(drive.eligible_branches)
            if student.branch and student.branch not in eligible:
                return jsonify({
                    'message': f'Your branch ({student.branch}) is not eligible for this drive',
                }), 400
        except (json.JSONDecodeError, TypeError):
            pass # Fallback if DB data corrupted(llm told to add)

    if drive.min_cgpa is not None and student.cgpa is not None:#cgpa check
        if float(student.cgpa) < float(drive.min_cgpa):
            return jsonify({
                'message': f'Your CGPA ({student.cgpa}) does not meet the minimum requirement ({drive.min_cgpa})',
            }), 400

    if drive.eligible_year is not None and student.year is not None:#year check
        if student.year != drive.eligible_year:
            return jsonify({
                'message': f'Your year ({student.year}) is not eligible for this drive (requires year {drive.eligible_year})',
            }), 400

    application = Application(#appn allow after all pass
        student_id=student.id,
        drive_id=drive_id,
        status='applied',
        application_date=now,
    )

    db.session.add(application)

    new_resume_path = data.get('resume_path', '').strip()#resume link add/edit
    if new_resume_path:
        student.resume_path = new_resume_path

    db.session.commit()
    
    # Invalidate caches
    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')
    cache_delete_pattern('students:*')

    return jsonify({
        'message': 'Application submitted successfully',
        'application_id': application.id,
    }), 201


@student_bp.route('/api/student/applications', methods=['GET'])#std site appn page ....appn view
@token_required
@role_required('student')
def list_applications():#view applided
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    results = (
        db.session.query(Application, PlacementDrive, CompanyProfile)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
        .filter(Application.student_id == student.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    applications = []
    for app, drive, company in results:
        placement = Placement.query.filter_by(application_id=app.id).first()
        applications.append({
            'id': app.id,
            'drive_id': drive.id,
            'job_title': drive.job_title,
            'location': drive.location,
            'salary': drive.salary,
            'eligible_branches': drive.eligible_branches,
            'min_cgpa': float(drive.min_cgpa) if drive.min_cgpa else None,
            'eligible_year': drive.eligible_year,
            'application_deadline': drive.application_deadline.isoformat() + 'Z' if drive.application_deadline else None,
            'interview_date': drive.interview_date.isoformat() + 'Z' if drive.interview_date else None,
            'company_id': company.id,
            'company_name': company.company_name,
            'company_industry': company.industry,
            'drive_status': drive.status,
            'status': app.status,
            'feedback': app.feedback,
            'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'interview_scheduled': app.interview_scheduled.isoformat() + 'Z' if app.interview_scheduled else None,
            'placement': {
                'id': placement.id,
                'position': placement.position,
                'salary': placement.salary,
                'joining_date': placement.joining_date.isoformat() + 'Z' if placement.joining_date else None,
                'is_accepted': placement.is_accepted,
                'created_at': placement.created_at.isoformat() + 'Z' if placement.created_at else None,
            } if placement else None,
        })

    return jsonify(applications), 200


@student_bp.route('/api/student/applications/<int:id>', methods=['GET'])#std site appn page single appn info
@token_required
@role_required('student')
def get_application(id):#view any speciifc appn info
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    result = (
        db.session.query(Application, PlacementDrive, CompanyProfile)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
        .filter(Application.id == id, Application.student_id == student.id)
        .first()
    )

    if not result:
        return jsonify({'error': 'Application not found'}), 404

    app, drive, company = result

    return jsonify({
        'id': app.id,
        'drive_id': drive.id,
        'job_title': drive.job_title,
        'job_description': drive.job_description,
        'company_id': company.id,
        'company_name': company.company_name,
        'location': drive.location,
        'salary': drive.salary,
        'company_industry': company.industry,
        'drive_status': drive.status,
        'status': app.status,
        'feedback': app.feedback,
        'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
        'interview_scheduled': app.interview_scheduled.isoformat() + 'Z' if app.interview_scheduled else None,
    }), 200




@student_bp.route('/api/student/history', methods=['GET'])#std site plmt histoty page
@token_required
@role_required('student')
def placement_history():#show acccept plmt by std
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    placements = Placement.query.filter_by(student_id=student.id).order_by(Placement.created_at.desc()).all()
    
    result = []
    for p in placements:
        result.append(p.to_dict())

    return jsonify(result), 200

##Imp logic part for plmt update logic


@student_bp.route('/api/student/placements/<int:placement_id>/accept', methods=['PUT'])#std site plmt accept by std get plcment to accpt by id
@token_required
@role_required('student')
def accept_placement(placement_id):#accept offer of plmt
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    placement = Placement.query.get(placement_id)
    if not placement or placement.student_id != student.id:
        return jsonify({'error': 'Placement not found'}), 404

    if placement.is_accepted:
        return jsonify({'error': 'Offer already accepted'}), 400

    from utils.upload import save_signature_file, save_base64_signature

    signature_path = None

    # 1. Check for multipart file upload
    if 'file' in request.files:
        try:
            signature_path = save_signature_file(request.files['file'])
        except Exception as e:
            return jsonify({'error': f'Signature upload failed: {str(e)}'}), 400
    elif 'signature' in request.files:
        try:
            signature_path = save_signature_file(request.files['signature'])
        except Exception as e:
            return jsonify({'error': f'Signature upload failed: {str(e)}'}), 400
    else:
        # 2. Check for JSON payload
        data = request.get_json(silent=True) or {}
        if data.get('signature_data'):
            try:
                signature_path = save_base64_signature(data['signature_data'])
            except Exception as e:
                return jsonify({'error': f'Signature processing failed: {str(e)}'}), 400
        elif data.get('signature_path'):
            signature_path = data['signature_path']
        elif student.signature_path:
            signature_path = student.signature_path

    # Signature is MANDATORY for student offer acceptance
    if not signature_path:
        return jsonify({
            'error': 'Signature is mandatory to accept this employment offer. Please upload or draw your signature (JPEG, PNG, etc.).'
        }), 400

    placement.student_signature_path = signature_path
    
    # Also save to student profile if not already set
    if not student.signature_path:
        student.signature_path = signature_path

    placement.is_accepted = True
    placement.accepted_at = datetime.utcnow()

    db.session.commit()
    
    # Invalidate caches
    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')
    cache_delete_pattern('students:*')

    return jsonify({
        'message': 'Offer accepted and signed successfully!',
        'placement': placement.to_dict()
    }), 200



@student_bp.route('/api/student/analytics', methods=['GET'])#std site anlytic page
@token_required
@role_required('student')
def student_analytics():#stats for dash chart ...60 s cache
    student = _get_student_profile()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    cache_key = f'student:analytics:{student.id}'
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    from sqlalchemy import func

#appn stats of std acc to status...#took llm help
    apps_by_status = db.session.query(Application.status, func.count(Application.id))\
                        .filter(Application.student_id == student.id)\
                        .group_by(Application.status).all()
    app_stats = {status: count for status, count in apps_by_status}

    data = {
        'applications': app_stats
    }
    cache_set(cache_key, data, expiry=60)#cache stter
    return jsonify(data), 200

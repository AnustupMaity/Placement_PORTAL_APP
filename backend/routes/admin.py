#admin route token+role needed

from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_
from extensions import db
from models.user import User
from models.company import CompanyProfile
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.application import Application
from models.placement import Placement
from utils.decorators import token_required, role_required
from utils.cache import cache_get, cache_set, cache_delete, cache_delete_pattern

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/dashboard', methods=['GET'])#STATS SHOWN IN ADMIN DAASH
@token_required
@role_required('admin')
def dashboard():
    cached = cache_get('admin:dashboard')#CACHE REFRESH 60S
    if cached is not None:
        return jsonify(cached), 200

    stats = {
        'total_students': StudentProfile.query.count(),
        'total_companies': CompanyProfile.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'total_applications': Application.query.count(),
        'pending_companies': CompanyProfile.query.filter_by(approval_status='pending').count(),
        'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
        'total_placements': Placement.query.count(),
    }

    cache_set('admin:dashboard', stats, expiry=60)#CACHE SET TO 60
    return jsonify(stats), 200


@admin_bp.route('/api/admin/analytics', methods=['GET'])#CHARTS ADMIN DASH
@token_required
@role_required('admin')
def admin_analytics():
    cached = cache_get('admin:analytics')#CACHE REFRESH 60S
    if cached is not None:
        return jsonify(cached), 200

    from sqlalchemy import func

    apps_by_status = db.session.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    app_stats = {status: count for status, count in apps_by_status}

    drives_by_status = db.session.query(PlacementDrive.status, func.count(PlacementDrive.id)).group_by(PlacementDrive.status).all()
    drive_stats = {status: count for status, count in drives_by_status}

    companies_by_status = db.session.query(CompanyProfile.approval_status, func.count(CompanyProfile.id)).group_by(CompanyProfile.approval_status).all()
    company_stats = {status: count for status, count in companies_by_status}

    # Chart Data: Placements by Branch
    from models.placement import Placement
    placements_by_branch = (
        db.session.query(StudentProfile.branch, func.count(Placement.id))
        .join(Placement, StudentProfile.id == Placement.student_id)
        .group_by(StudentProfile.branch)
        .all()
    )
    branch_labels = [row[0] for row in placements_by_branch if row[0]]
    branch_data = [row[1] for row in placements_by_branch if row[0]]

    # Chart Data: Top Recruiters
    top_recruiters = (
        db.session.query(CompanyProfile.company_name, func.count(Placement.id).label('hires'))
        .join(Placement, CompanyProfile.id == Placement.company_id)
        .group_by(CompanyProfile.company_name)
        .order_by(db.desc('hires'))
        .limit(5)
        .all()
    )
    recruiter_labels = [row[0] for row in top_recruiters]
    recruiter_data = [row[1] for row in top_recruiters]

    # Chart Data: Salary trends (by year/drive) - simplified to avg salary per company
    salary_trends_raw = (
        db.session.query(CompanyProfile.company_name, PlacementDrive.salary)
        .join(PlacementDrive, CompanyProfile.id == PlacementDrive.company_id)
        .all()
    )
    # Process in python for DB compatibility
    company_salaries = {}
    for comp, sal_str in salary_trends_raw:
        if not sal_str: continue
        try:
            val = float(sal_str)
            if val > 0:
                if comp not in company_salaries:
                    company_salaries[comp] = []
                company_salaries[comp].append(val)
        except (ValueError, TypeError):
            pass

    parsed_salaries = []
    salary_labels = []
    for comp, salaries in company_salaries.items():
        if len(salaries) > 0:
            avg_sal = sum(salaries) / len(salaries)
            salary_labels.append(comp)
            parsed_salaries.append(round(avg_sal, 2))

    data = {
        'applications': app_stats,
        'drives': drive_stats,
        'companies': company_stats,
        'charts': {
            'placements_by_branch': {
                'labels': branch_labels,
                'data': branch_data
            },
            'top_recruiters': {
                'labels': recruiter_labels,
                'data': recruiter_data
            },
            'salary_trends': {
                'labels': salary_labels,
                'data': parsed_salaries
            }
        }
    }

    cache_set('admin:analytics', data, expiry=60)#CACHE SET TO 60
    return jsonify(data), 200

@admin_bp.route('/api/admin/profile', methods=['GET'])
@token_required
@role_required('admin')
def get_profile():
    user = User.query.get(g.current_user.id)
    return jsonify({
        'institute_name': user.institute_name,
        'institute_address': user.institute_address,
        'institute_logo_url': user.institute_logo_url
    }), 200

@admin_bp.route('/api/admin/profile', methods=['PUT'])
@token_required
@role_required('admin')
def update_profile():
    user = User.query.get(g.current_user.id)
    data = request.get_json(silent=True) or {}
    
    if 'institute_name' in data:
        user.institute_name = data['institute_name']
    if 'institute_address' in data:
        user.institute_address = data['institute_address']
    if 'institute_logo_url' in data:
        user.institute_logo_url = data['institute_logo_url']
        
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200


@admin_bp.route('/api/admin/companies', methods=['GET'])#admin comapny page
@token_required
@role_required('admin')
def list_companies():

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    query = db.session.query(CompanyProfile, User).join(
        User, CompanyProfile.user_id == User.id
    )

    if search:
        pattern = f'%{search}%'
        query = query.filter(
            or_(
                CompanyProfile.company_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    if status:
        query = query.filter(CompanyProfile.approval_status == status)

    results = query.all()

    companies = []
    for company, user in results:
        companies.append({
            'id': company.id,
            'user_id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'company_name': company.company_name,
            'industry': company.industry,
            'website': company.website,
            'location': company.location,
            'description': company.description,
            'hr_name': company.hr_name,
            'hr_email': company.hr_email,
            'hr_phone': company.hr_phone,
            'approval_status': company.approval_status,
            'is_blacklisted': company.is_blacklisted,
            'created_at': company.created_at.isoformat() + 'Z' if company.created_at else None,
        })

    return jsonify(companies), 200


@admin_bp.route('/api/admin/companies/<int:id>/approve', methods=['PUT'])#approve  comp 
@token_required
@role_required('admin')
def approve_company(id):
    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({'error': 'company not found'}), 404

    company.approval_status = 'approved'
    
    drives = PlacementDrive.query.filter_by(company_id=id, status='pending').all()
    for drive in drives:
        drive.status = 'approved'
        
    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('companies:*')
    cache_delete_pattern('drives:*')

    return jsonify({'message': 'company approved '}), 200


@admin_bp.route('/api/admin/companies/<int:id>/reject', methods=['PUT'])#reject comp 
@token_required
@role_required('admin')
def reject_company(id):
    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    company.approval_status = 'rejected'
    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('companies:*')

    return jsonify({'message': 'company rejected '}), 200


@admin_bp.route('/api/admin/companies/<int:id>/blacklist', methods=['PUT'])#blacklist
@token_required
@role_required('admin')
def toggle_blacklist_company(id):
    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({'error': 'company not found'}), 404

    user = User.query.get(company.user_id)
    if not user:
        return jsonify({'error': ' user not found'}), 404

    company.is_blacklisted = not company.is_blacklisted

    if company.is_blacklisted:
        user.is_active = False
        drives = PlacementDrive.query.filter_by(company_id=id).all()
        for drive in drives:
            if drive.status != 'rejected' and drive.status != 'closed':
                drive.status = 'cancelled'
    else:
        user.is_active = True
        # AUTO-RESUME CANCELLED DRIVES IF DEADLINE HAS NOT PASSED 
        # from datetime import datetime
        # drives = PlacementDrive.query.filter_by(company_id=id, status='cancelled').all()
        # for drive in drives:
        #     if drive.application_deadline and drive.application_deadline.date() >= datetime.utcnow().date():
        #         drive.status = 'approved'

    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('companies:*')
    cache_delete_pattern('drives:*')

    action = 'blacklisted' if company.is_blacklisted else 'un-blacklisted'
    return jsonify({'message': f'Company {action} successfully'}), 200


@admin_bp.route('/api/admin/companies/<int:id>', methods=['DELETE'])#deactive...non reversible
@token_required
@role_required('admin')
def delete_company(id):
    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({'error': 'company not found'}), 404

    user = User.query.get(company.user_id)
    if not user:
        return jsonify({'error': ' user not found'}), 404

    user.is_active = False
    
    # HARD DELETE 
    # Uncomment   below and comment  'user.is_active = False'  
    # to completely wipe this company and all their associated data from the DB.
    # db.session.delete(company)
    # db.session.delete(user)

    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('companies:*')

    return jsonify({'message': 'company deleted '}), 200




@admin_bp.route('/api/admin/students', methods=['GET'])#admin student
@token_required
@role_required('admin')
def list_students():
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()

    query = db.session.query(StudentProfile, User).join(
        User, StudentProfile.user_id == User.id
    )

    if search:
        pattern = f'%{search}%'
        query = query.filter(
            or_(
                StudentProfile.full_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    if branch:
        query = query.filter(StudentProfile.branch == branch)

    results = query.all()

    students = []
    for student, user in results:
        students.append({
            'id': student.id,
            'user_id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'full_name': student.full_name,
            'branch': student.branch,
            'year': student.year,
            'cgpa': float(student.cgpa) if student.cgpa is not None else None,
            'skills': student.skills,
            'phone': student.phone,
            'resume_path': student.resume_path,
            'is_blacklisted': student.is_blacklisted,
            'created_at': student.created_at.isoformat() + 'Z' if student.created_at else None,
        })

    return jsonify(students), 200


@admin_bp.route('/api/admin/students/<int:id>/blacklist', methods=['PUT'])#student blacklist
@token_required
@role_required('admin')
def toggle_blacklist_student(id):
    student = StudentProfile.query.get(id)
    if not student:
        return jsonify({'error': 'student not found'}), 404

    user = User.query.get(student.user_id)
    if not user:
        return jsonify({'error': ' user not found'}), 404

    student.is_blacklisted = not student.is_blacklisted

    if student.is_blacklisted:
        user.is_active = False
    else:
        user.is_active = True
        #  UNCOMMENT  TO AUTO-RESUME CANCELLED DRIVES IF DEADLINE HAS NOT PASSED 
        # from datetime import datetime
        # drives = PlacementDrive.query.filter_by(company_id=id, status='cancelled').all()
        # for drive in drives:
        #     if drive.application_deadline and drive.application_deadline.date() >= datetime.utcnow().date():
        #         drive.status = 'approved'

    db.session.commit()

    return jsonify({
        'message': f'Student {"blacklisted" if student.is_blacklisted else "un-blacklisted"} successfully',
    }), 200

@admin_bp.route('/api/admin/students/<int:id>', methods=['DELETE'])#delete but db not affted remove from froennd
@token_required
@role_required('admin')
def delete_student(id):
    student = StudentProfile.query.get(id)
    if not student:
        return jsonify({'error': 'student not found'}), 404

    user = User.query.get(student.user_id)
    if not user:
        return jsonify({'error': ' user not found'}), 404

    user.is_active = False
    
    #  HARD DELETE 
    # Uncomment   below and comment  'user.is_active = False'  
    # to completely wipe this student and all their associated data from the DB.
    # db.session.delete(student)
    # db.session.delete(user)

    db.session.commit()

    cache_delete('admin:dashboard')

    return jsonify({'message': 'student deleted '}), 200

@admin_bp.route('/api/admin/students/<int:id>/details', methods=['GET'])
@token_required
@role_required('admin')
def get_student_details(id):
    student = StudentProfile.query.get(id)
    if not student:
        return jsonify({'error': 'student not found'}), 404
        
    user = User.query.get(student.user_id)
        
    apps = Application.query.filter_by(student_id=student.id).all()
    applications = []
    for app in apps:
        drive = PlacementDrive.query.get(app.drive_id)
        company = CompanyProfile.query.get(drive.company_id) if drive else None
        
        # Check for placement details
        placement = Placement.query.filter_by(application_id=app.id).first()
        
        applications.append({
            'id': app.id,
            'drive_title': drive.job_title if drive else 'Unknown',
            'company_name': company.company_name if company else 'Unknown',
            'status': app.status,
            'feedback': app.feedback,
            'date_applied': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'placement': placement.to_dict() if placement else None
        })
        
    student_dict = student.to_dict()
    student_dict['email'] = user.email if user else None
        
    return jsonify({
        'student': student_dict,
        'applications': applications
    }), 200


@admin_bp.route('/api/admin/drives', methods=['GET'])
@token_required
@role_required('admin')
def list_drives():
    status = request.args.get('status', '').strip()

    query = db.session.query(PlacementDrive, CompanyProfile).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    )

    if status:
        query = query.filter(PlacementDrive.status == status)

    results = query.all()

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
            'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
        })

    return jsonify(drives), 200


@admin_bp.route('/api/admin/drives/<int:id>/approve', methods=['PUT'])#approve drive
@token_required
@role_required('admin')
def approve_drive(id):
    drive = PlacementDrive.query.get(id)
    if not drive:
        return jsonify({'error': 'drive not found'}), 404

    drive.status = 'approved'
    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')

    return jsonify({'message': 'drive approved '}), 200


@admin_bp.route('/api/admin/drives/<int:id>/reject', methods=['PUT'])#reject drive
@token_required
@role_required('admin')
def reject_drive(id):
    drive = PlacementDrive.query.get(id)
    if not drive:
        return jsonify({'error': 'drive not found'}), 404

    drive.status = 'rejected'
    db.session.commit()

    cache_delete('admin:dashboard')
    cache_delete_pattern('drives:*')

    return jsonify({'message': 'drive rejected '}), 200


#admin site placemnt page
@admin_bp.route('/api/admin/placements', methods=['GET'])
@token_required
@role_required('admin')
def list_placements():
    placements = Placement.query.order_by(Placement.created_at.desc()).all()
    result = [p.to_dict() for p in placements]
    return jsonify(result), 200

#admin site application page 
@admin_bp.route('/api/admin/applications', methods=['GET'])
@token_required
@role_required('admin')
def list_applications():
    status = request.args.get('status', '').strip()
    drive_id = request.args.get('drive_id', type=int)

    query = (
        db.session.query(Application, StudentProfile, PlacementDrive, CompanyProfile)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
    )

    if status:
        query = query.filter(Application.status == status)
    if drive_id:
        query = query.filter(Application.drive_id == drive_id)

    results = query.all()

    applications = []
    for app, student, drive, company in results:
        applications.append({
            'id': app.id,
            'student_id': student.id,
            'student_name': student.full_name,
            'drive_id': drive.id,
            'drive_title': drive.job_title,
            'company_id': company.id,
            'company_name': company.company_name,
            'status': app.status,
            'feedback': app.feedback,
            'application_date': app.application_date.isoformat() + 'Z' if app.application_date else None,
            'interview_scheduled': app.interview_scheduled.isoformat() + 'Z' if app.interview_scheduled else None,
        })

    return jsonify(applications), 200


#backgrond work ...reqd by admin site ++ manual sending of email
@admin_bp.route('/api/admin/trigger/daily-reminders', methods=['POST'])
@token_required
@role_required('admin')

def trigger_daily_reminders():#manual daily reminder send celery
    from tasks.reminders import send_daily_reminders
    send_daily_reminders.delay()
    return jsonify({'message': 'daily reminders  triggered '}), 200


@admin_bp.route('/api/admin/trigger/monthly-report', methods=['POST'])
@token_required
@role_required('admin')

def trigger_monthly_report():#month repost send manual celery
    from tasks.reports import generate_monthly_report
    generate_monthly_report.delay()
    return jsonify({'message': 'monthly report  triggered '}), 200
@admin_bp.route('/api/admin/drives/<int:id>/details', methods=['GET'])
@token_required
@role_required('admin')
def get_drive_details(id):
    drive = PlacementDrive.query.get(id)
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404
        
    company = CompanyProfile.query.get(drive.company_id)
    
    apps = Application.query.filter_by(drive_id=id).all()
    applications = []
    
    stats = {
        'total': len(apps),
        'applied': 0,
        'shortlisted': 0,
        'selected': 0,
        'rejected': 0
    }
    
    for app in apps:
        student = StudentProfile.query.get(app.student_id)
        if app.status in stats:
            stats[app.status] += 1
            
        placement = Placement.query.filter_by(application_id=app.id).first()
        
        applications.append({
            'id': app.id,
            'student_id': student.id if student else None,
            'student_name': student.full_name if student else 'Unknown',
            'roll_number': student.roll_number if student else 'Unknown',
            'branch': student.branch if student else 'Unknown',
            'cgpa': float(student.cgpa) if student and student.cgpa else None,
            'status': app.status,
            'feedback': app.feedback,
            'date_applied': app.application_date.isoformat() + 'Z',
            'placement': placement.to_dict() if placement else None
        })
        
    return jsonify({
        'drive': drive.to_dict() if hasattr(drive, 'to_dict') else {
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
            'created_at': drive.created_at.isoformat() + 'Z' if drive.created_at else None,
        },
        'company': company.to_dict() if company and hasattr(company, 'to_dict') else {
            'company_name': company.company_name if company else 'Unknown'
        },
        'stats': stats,
        'applications': applications
    }), 200
@admin_bp.route('/api/admin/applications/<int:id>/details', methods=['GET'])
@token_required
@role_required('admin')
def get_application_details(id):
    app = Application.query.get(id)
    if not app:
        return jsonify({'error': 'Application not found'}), 404
        
    student = StudentProfile.query.get(app.student_id)
    drive = PlacementDrive.query.get(app.drive_id)
    company = CompanyProfile.query.get(drive.company_id) if drive else None
    placement = Placement.query.filter_by(application_id=app.id).first()
    
    return jsonify({
        'application': app.to_dict() if hasattr(app, 'to_dict') else {
            'id': app.id,
            'status': app.status,
            'application_date': app.application_date.isoformat() + 'Z',
        },
        'student': student.to_dict() if student and hasattr(student, 'to_dict') else {
            'id': student.id,
            'full_name': student.full_name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'cgpa': float(student.cgpa) if student.cgpa else None,
            'resume_path': student.resume_path
        },
        'drive': drive.to_dict() if drive and hasattr(drive, 'to_dict') else {
            'id': drive.id,
            'job_title': drive.job_title,
            'location': drive.location,
            'salary': drive.salary
        },
        'company': company.to_dict() if company and hasattr(company, 'to_dict') else {
            'company_name': company.company_name if company else 'Unknown'
        },
        'placement': placement.to_dict() if placement else None
    }), 200
@admin_bp.route('/api/admin/placements/<int:id>/details', methods=['GET'])
@token_required
@role_required('admin')
def get_placement_details(id):
    placement = Placement.query.get(id)
    if not placement:
        return jsonify({'error': 'Placement not found'}), 404
        
    app = Application.query.get(placement.application_id) if placement.application_id else None
    
    student = StudentProfile.query.get(app.student_id) if app and app.student_id else None
    drive = PlacementDrive.query.get(app.drive_id) if app and app.drive_id else None
    company = CompanyProfile.query.get(drive.company_id) if drive and drive.company_id else None
    
    return jsonify({
        'placement': placement.to_dict() if hasattr(placement, 'to_dict') else {
            'id': placement.id,
            'salary': placement.salary,
            'is_accepted': placement.is_accepted
        },
        'application': app.to_dict() if app and hasattr(app, 'to_dict') else {
            'id': app.id if app else None,
            'status': app.status if app else None,
            'application_date': app.application_date.isoformat() + 'Z' if app else None,
        },
        'student': student.to_dict() if student and hasattr(student, 'to_dict') else {
            'id': student.id if student else None,
            'full_name': student.full_name if student else 'Unknown',
            'roll_number': student.roll_number if student else None,
            'branch': student.branch if student else None,
            'cgpa': float(student.cgpa) if student and student.cgpa else None,
            'resume_path': student.resume_path if student else None
        },
        'drive': drive.to_dict() if drive and hasattr(drive, 'to_dict') else {
            'id': drive.id if drive else None,
            'job_title': drive.job_title if drive else 'Unknown',
            'location': drive.location if drive else None,
            'salary': drive.salary if drive else None
        },
        'company': company.to_dict() if company and hasattr(company, 'to_dict') else {
            'company_name': company.company_name if company else 'Unknown'
        }
    }), 200


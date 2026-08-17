#CSV EXPORT

import os
import csv
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app, send_from_directory
from extensions import db
from models.application import Application
from models.drive import PlacementDrive
from models.company import CompanyProfile
from models.student import StudentProfile
from models.placement import Placement
from utils.decorators import token_required, role_required

export_bp = Blueprint('export', __name__)



@export_bp.route('/api/export/applications', methods=['POST'])
@token_required
@role_required('student')
def export_applications():#BG CELERY APPN  CSV EXPORT 
    student = StudentProfile.query.filter_by(user_id=g.current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    try:
        from tasks.exports import export_applications_csv
        task = export_applications_csv.delay(student.id)
        return jsonify({
            'message': 'Export task started',
            'task_id': task.id,
        }), 202
    except Exception as e:
        return jsonify({'error': f'Celery background worker is not available: {str(e)}'}), 500


@export_bp.route('/api/export/company/applications', methods=['POST'])
@token_required
@role_required('company')
def export_company_applications():
    company = CompanyProfile.query.filter_by(user_id=g.current_user.id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    try:
        from tasks.exports import export_company_applications_csv
        task = export_company_applications_csv.delay(company.id)
        return jsonify({
            'message': 'Export task started',
            'task_id': task.id,
        }), 202
    except Exception as e:
        return jsonify({'error': f'Celery background worker is not available: {str(e)}'}), 500


@export_bp.route('/api/export/admin/applications', methods=['POST'])
@token_required
@role_required('admin')
def export_admin_applications():
    try:
        from tasks.exports import export_admin_applications_csv
        task = export_admin_applications_csv.delay()
        return jsonify({
            'message': 'Export task started',
            'task_id': task.id,
        }), 202
    except Exception as e:
        return jsonify({'error': f'Celery background worker is not available: {str(e)}'}), 500


@export_bp.route('/api/export/status/<task_id>', methods=['GET'])
@token_required
def export_status(task_id):#CSV  EXPORT BG CELERY STATUS
    try:
        from app import celery
        task = celery.AsyncResult(task_id)

        response = {
            'task_id': task_id,
            'status': task.state,
        }

        if task.state == 'SUCCESS':
            response['result'] = task.result
        elif task.state == 'FAILURE':
            response['error'] = str(task.info)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'message': f'Unable to check task status: {str(e)}',
        }), 500


@export_bp.route('/api/export/download/<filename>', methods=['GET'])
@token_required
def download_export(filename):#used to download csv after clicking download btton.....chatgpt help taken to write the code
    if '..' in filename or '/' in filename or '\\' in filename:#prevent directory traversal
        return jsonify({'error': 'Invalid filename'}), 400
    if not filename.endswith('.csv'):#only csv allow
        return jsonify({'error': 'Invalid file type'}), 400

    export_dir = os.path.join(current_app.root_path, 'exports')

    filepath = os.path.join(export_dir, filename)#does file exist??
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory(
        export_dir,
        filename,
        as_attachment=True,
        mimetype='text/csv',
    )


@export_bp.route('/api/export/offer_letter/<int:placement_id>', methods=['GET'])
@token_required
def export_offer_letter(placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({'error': 'Placement not found'}), 404

    company = CompanyProfile.query.get(placement.company_id)
    student = StudentProfile.query.get(placement.student_id)

    if g.current_user.role == 'student':
        student_profile = StudentProfile.query.filter_by(user_id=g.current_user.id).first()
        if not student_profile or placement.student_id != student_profile.id:
            return jsonify({'error': 'Unauthorized access to offer letter'}), 403
    elif g.current_user.role == 'company':
        company_profile = CompanyProfile.query.filter_by(user_id=g.current_user.id).first()
        if not company_profile or placement.company_id != company_profile.id:
            return jsonify({'error': 'Unauthorized access to offer letter'}), 403

    from flask import render_template, make_response
    from xhtml2pdf import pisa
    from io import BytesIO
    from utils.upload import get_signature_base64

    today_date = datetime.utcnow().strftime('%B %d, %Y')
    joining_date = placement.joining_date.strftime('%B %d, %Y') if placement.joining_date else 'To be mutually agreed upon'

    student_name = student.full_name if student else (placement.application.student.full_name if placement.application and placement.application.student else "Candidate")
    company_name = company.company_name if company else (placement.application.drive.company.company_name if placement.application and placement.application.drive and placement.application.drive.company else "Organization")
    company_location = company.location if company else "Campus Placements"
    company_hr_name = company.hr_name if company and company.hr_name else "Human Resources"

    company_sig_path = placement.company_signature_path or (company.signature_path if company else None)
    company_signature_data = get_signature_base64(company_sig_path)

    placement_dict = placement.to_dict()
    placement_dict['student_name'] = student_name
    placement_dict['company_name'] = company_name

    try:
        html_content = render_template(
            'offer_letter.html',
            placement=placement_dict,
            student_name=student_name,
            company_name=company_name,
            company_location=company_location,
            company_hr_name=company_hr_name,
            today_date=today_date,
            joining_date=joining_date,
            company_signature=company_signature_data
        )

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_buffer)
        if pisa_status.err:
            current_app.logger.error(f"xhtml2pdf error generating offer letter: {pisa_status.err}")
            return jsonify({'error': 'Failed to generate PDF offer letter'}), 500

        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=Offer_Letter_{placement.id}.pdf'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error in export_offer_letter: {e}")
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


@export_bp.route('/api/export/acceptance_letter/<int:placement_id>', methods=['GET'])
@token_required
def export_acceptance_letter(placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        return jsonify({'error': 'Placement not found'}), 404
        
    if not placement.is_accepted:
        return jsonify({'error': 'Offer has not been accepted yet'}), 400

    company = CompanyProfile.query.get(placement.company_id)
    student = StudentProfile.query.get(placement.student_id)

    if g.current_user.role == 'student':
        student_profile = StudentProfile.query.filter_by(user_id=g.current_user.id).first()
        if not student_profile or placement.student_id != student_profile.id:
            return jsonify({'error': 'Unauthorized access to acceptance letter'}), 403
    elif g.current_user.role == 'company':
        company_profile = CompanyProfile.query.filter_by(user_id=g.current_user.id).first()
        if not company_profile or placement.company_id != company_profile.id:
            return jsonify({'error': 'Unauthorized access to acceptance letter'}), 403

    from flask import render_template, make_response
    from xhtml2pdf import pisa
    from io import BytesIO
    from utils.upload import get_signature_base64

    accepted_date = placement.accepted_at.strftime('%B %d, %Y') if placement.accepted_at else datetime.utcnow().strftime('%B %d, %Y')
    student_name = student.full_name if student else (placement.application.student.full_name if placement.application and placement.application.student else "Candidate")
    student_roll = student.roll_number if student and student.roll_number else "N/A"
    student_branch = student.branch if student and student.branch else "N/A"
    company_name = company.company_name if company else (placement.application.drive.company.company_name if placement.application and placement.application.drive and placement.application.drive.company else "Organization")

    student_sig_path = placement.student_signature_path or (student.signature_path if student else None)
    student_signature_data = get_signature_base64(student_sig_path)

    placement_dict = placement.to_dict()
    placement_dict['student_name'] = student_name
    placement_dict['company_name'] = company_name

    try:
        html_content = render_template(
            'acceptance_letter.html',
            placement=placement_dict,
            student_name=student_name,
            student_roll=student_roll,
            student_branch=student_branch,
            company_name=company_name,
            accepted_date=accepted_date,
            student_signature=student_signature_data
        )

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_buffer)
        if pisa_status.err:
            current_app.logger.error(f"xhtml2pdf error generating acceptance letter: {pisa_status.err}")
            return jsonify({'error': 'Failed to generate PDF acceptance letter'}), 500

        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=Acceptance_Letter_{placement.id}.pdf'
        return response
    except Exception as e:
        current_app.logger.error(f"Error in export_acceptance_letter: {e}")
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

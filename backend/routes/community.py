from flask import Blueprint, request, jsonify, g
from extensions import db
from models.community import InterviewExperience
from models.company import CompanyProfile
from models.student import StudentProfile
from utils.decorators import token_required

community_bp = Blueprint('community', __name__)

@community_bp.route('/api/community/experiences', methods=['GET'])
@token_required
def list_experiences():
    company_id = request.args.get('company_id', type=int)
    
    query = InterviewExperience.query.filter_by(status='approved')
    if company_id:
        query = query.filter_by(company_id=company_id)
        
    experiences = query.order_by(InterviewExperience.created_at.desc()).all()
    return jsonify([exp.to_dict() for exp in experiences]), 200

@community_bp.route('/api/community/experiences', methods=['POST'])
@token_required
def create_experience():
    if g.current_user.role != 'student':
        return jsonify({'error': 'Only students can post interview experiences.'}), 403

    student = StudentProfile.query.filter_by(user_id=g.current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found.'}), 404

    data = request.get_json(silent=True) or {}
    
    company_id = data.get('company_id')
    title = data.get('title')
    content = data.get('content')
    role = data.get('role')
    is_anonymous = data.get('is_anonymous', False)
    
    if not company_id or not title or not content:
        return jsonify({'error': 'Company, title, and content are required.'}), 400

    exp = InterviewExperience(
        student_id=student.id,
        company_id=company_id,
        title=title,
        content=content,
        role=role,
        is_anonymous=is_anonymous,
        status='approved' # Auto-approve for now, could be 'pending' for admin review
    )
    db.session.add(exp)
    db.session.commit()
    
    return jsonify({'message': 'Experience posted successfully!', 'experience': exp.to_dict()}), 201

@community_bp.route('/api/community/experiences/<int:exp_id>', methods=['DELETE'])
@token_required
def delete_experience(exp_id):
    exp = InterviewExperience.query.get(exp_id)
    if not exp:
        return jsonify({'error': 'Experience not found.'}), 404

    # Allow admin or the author to delete
    if g.current_user.role == 'admin':
        pass
    elif g.current_user.role == 'student':
        student = StudentProfile.query.filter_by(user_id=g.current_user.id).first()
        if not student or exp.student_id != student.id:
            return jsonify({'error': 'Unauthorized to delete this experience.'}), 403
    else:
        return jsonify({'error': 'Unauthorized.'}), 403

    db.session.delete(exp)
    db.session.commit()
    
    return jsonify({'message': 'Experience deleted.'}), 200

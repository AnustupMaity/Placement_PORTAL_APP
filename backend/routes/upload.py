import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app, g
from utils.decorators import token_required
from utils.upload import save_signature_file, save_base64_signature, get_upload_dir

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload/signature', methods=['POST'])
@token_required
def upload_signature():
    """
    Upload a signature image via multipart form-data ('file' or 'signature')
    or JSON body with 'signature_data' (Base64 data URI).
    """
    try:
        file_url = None
        
        # Check multipart form-data
        if 'file' in request.files:
            file = request.files['file']
            file_url = save_signature_file(file, type='signature')
        elif 'signature' in request.files:
            file = request.files['signature']
            file_url = save_signature_file(file, type='signature')
        else:
            # Check JSON body
            data = request.get_json(silent=True) or {}
            signature_data = data.get('signature_data') or data.get('signature')
            if signature_data:
                file_url = save_base64_signature(signature_data, type='signature')
            else:
                return jsonify({'error': 'No signature file or data provided.'}), 400

        return jsonify({
            'message': 'Signature uploaded successfully',
            'file_url': file_url,
            'filename': os.path.basename(file_url)
        }), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to process signature: {str(e)}'}), 500


@upload_bp.route('/api/uploads/signatures/<filename>', methods=['GET'])
def serve_signature(filename):
    """Serve uploaded signature image files securely."""
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
        
    upload_dir = get_upload_dir(type='signature')
    filepath = os.path.join(upload_dir, filename)
    if not os.path.isfile(filepath):
        return jsonify({'error': 'Signature file not found'}), 404

    return send_from_directory(upload_dir, filename)

@upload_bp.route('/api/upload/image', methods=['POST'])
@token_required
def upload_image():
    """
    Upload a general image (profile pic, logo) via multipart form-data
    """
    try:
        file_url = None
        
        if 'file' in request.files:
            file = request.files['file']
            file_url = save_signature_file(file, type='image')
        elif 'image' in request.files:
            file = request.files['image']
            file_url = save_signature_file(file, type='image')
        else:
            data = request.get_json(silent=True) or {}
            image_data = data.get('image_data') or data.get('image')
            if image_data:
                file_url = save_base64_signature(image_data, type='image')
            else:
                return jsonify({'error': 'No image file or data provided.'}), 400

        return jsonify({
            'message': 'Image uploaded successfully',
            'file_url': file_url,
            'filename': os.path.basename(file_url)
        }), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@upload_bp.route('/api/uploads/images/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve uploaded general images (logos, profiles)."""
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
        
    upload_dir = get_upload_dir(type='image')
    filepath = os.path.join(upload_dir, filename)
    if not os.path.isfile(filepath):
        return jsonify({'error': 'Image file not found'}), 404

    return send_from_directory(upload_dir, filename)

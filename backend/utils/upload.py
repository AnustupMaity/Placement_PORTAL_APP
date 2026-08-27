import os
import uuid
import base64
import mimetypes
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_SIGNATURE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_SIGNATURE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def get_upload_dir(type='signature'):
    """Get or create the specific upload directory."""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    folder = 'signatures' if type == 'signature' else 'images'
    upload_dir = os.path.join(backend_dir, 'uploads', folder)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def allowed_file(filename):
    """Check if the filename has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_SIGNATURE_EXTENSIONS

def save_signature_file(file_storage, type='signature'):
    """Save an uploaded FileStorage object securely and return its relative URL/path."""
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided.")

    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError(f"Invalid file type. Allowed formats: {', '.join(ALLOWED_SIGNATURE_EXTENSIONS).upper()}")

    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)
    if file_size > MAX_SIGNATURE_SIZE_BYTES:
        raise ValueError("File size exceeds maximum allowed limit of 5MB.")

    ext = filename.rsplit('.', 1)[1].lower()
    prefix = 'sig_' if type == 'signature' else 'img_'
    unique_filename = f"{prefix}{uuid.uuid4().hex[:12]}.{ext}"
    upload_dir = get_upload_dir(type)
    filepath = os.path.join(upload_dir, unique_filename)
    
    file_storage.save(filepath)
    route_folder = 'signatures' if type == 'signature' else 'images'
    return f"/api/uploads/{route_folder}/{unique_filename}"

def save_base64_signature(data_uri, type='signature'):
    """Save a Base64 data URI (e.g. from canvas or FileReader) as an image file."""
    if not data_uri or not isinstance(data_uri, str):
        raise ValueError("Invalid signature data.")

    if ',' in data_uri:
        header, encoded = data_uri.split(',', 1)
    else:
        header, encoded = '', data_uri

    ext = 'png'
    if 'image/jpeg' in header or 'image/jpg' in header:
        ext = 'jpg'
    elif 'image/webp' in header:
        ext = 'webp'
    elif 'image/png' in header:
        ext = 'png'

    try:
        image_data = base64.b64decode(encoded)
    except Exception:
        raise ValueError("Corrupt base64 data.")

    if len(image_data) > MAX_SIGNATURE_SIZE_BYTES:
        raise ValueError("Image exceeds maximum allowed limit of 5MB.")

    prefix = 'sig_' if type == 'signature' else 'img_'
    unique_filename = f"{prefix}{uuid.uuid4().hex[:12]}.{ext}"
    upload_dir = get_upload_dir(type)
    filepath = os.path.join(upload_dir, unique_filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    route_folder = 'signatures' if type == 'signature' else 'images'
    return f"/api/uploads/{route_folder}/{unique_filename}"

def get_signature_base64(signature_path, type='signature'):
    """
    Given a stored URL/path (e.g. /api/uploads/signatures/xyz.png),
    read the file from disk and return a Base64 Data URI for embedding in HTML/PDF.
    Returns None if file does not exist.
    """
    if not signature_path:
        return None

    if signature_path.startswith('data:image'):
        return signature_path

    filename = os.path.basename(signature_path)
    upload_dir = get_upload_dir(type)
    filepath = os.path.join(upload_dir, filename)

    if not os.path.isfile(filepath):
        return None

    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = 'image/png'

    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            b64_str = base64.b64encode(data).decode('utf-8')
            return f"data:{mime_type};base64,{b64_str}"
    except Exception:
        return None

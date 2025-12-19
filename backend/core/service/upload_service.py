import os
from werkzeug.utils import secure_filename
from core.parsers.cv import get_available_links

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_upload_folder():
    """Delete all files in the upload folder"""
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def handle_file_upload(files):
    """Handle multiple file uploads after clearing the folder"""
    clear_upload_folder()

    if not files or files[0].filename == '':
        return {"error": "No files selected"}, 400

    uploaded_files = []
    errors = []

    for file in files:
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # prevent duplicates
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                counter += 1

            try:
                file.save(filepath)
                uploaded_files.append(filename)
            except Exception as e:
                errors.append(f"Failed to save {file.filename}: {str(e)}")
        else:
            errors.append(f"{file.filename} is not a valid PDF or DOCX file")

    if uploaded_files:
        response = {
            "uploaded": len(uploaded_files),
            "files": uploaded_files
        }
        if errors:
            response["errors"] = errors
        return response, 200
    else:
        return {
            "error": "No files were uploaded",
            "errors": errors
        }, 400
    

def get_file_link_counts():
    link_summary = {"uploaded_files": 0, "link_counts": {}}

    for file in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.pdf', '.docx']:
            link_summary["uploaded_files"] += 1
            links = get_available_links(filepath)
            for link_type, is_present in links.items():
                if is_present:
                    link_summary["link_counts"].setdefault(link_type, 0)
                    link_summary["link_counts"][link_type] += 1

    return link_summary
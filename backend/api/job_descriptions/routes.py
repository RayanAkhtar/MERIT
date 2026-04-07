from flask import Blueprint, jsonify, request
from core.supabase import supabase

job_descriptions_bp = Blueprint("job_descriptions", __name__)

@job_descriptions_bp.route("/save-cvs", methods=["POST"])
def save_cvs():
    """Attempt to save multiple CVs. Returns error as it's not implemented yet."""
    if 'files' not in request.files or not request.files.getlist('files'):
        return jsonify({"error": "No files provided"}), 400
    return jsonify({"error": "Saving CVs is not implemented yet."}), 501

@job_descriptions_bp.route("/get-job-descriptions", methods=["GET"])
def get_job_descriptions():
    """Fetch all saved Job Descriptions from Supabase"""
    try:
        if not supabase:
            return jsonify({"error": "Database connection not established"}), 500
            
        response = supabase.table("job_requirements").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"ERROR fetching job descriptions: {str(e)}")
        return jsonify({"error": f"Failed to fetch from database: {str(e)}"}), 500

def _group_metrics(metrics):
    """Internal helper to structure flat metric lists into category-based groups for Supabase storage."""
    list_type_cats = ["Languages", "Technologies", "Soft Skills", "Responsibilities", "Requirements", "Education"]
    grouped_metrics = {}
    for m in metrics:
        cat = m.get("category", "General")
        val = m.get("value", "")
        
        if cat not in grouped_metrics:
            cat_type = "list" if cat in list_type_cats else "key-value"
            grouped_metrics[cat] = {
                "type": cat_type,
                "value": []
            }
        
        if grouped_metrics[cat]["type"] == "list":
            if val: grouped_metrics[cat]["value"].append(val)
        else:
            item = {k: v for k, v in m.items() if k != 'category'}
            grouped_metrics[cat]["value"].append(item)
    return grouped_metrics

@job_descriptions_bp.route("/save-job-description", methods=["POST"])
def save_job_description():
    """Save finalised Job Description to Supabase"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description")
        metrics = data.get("metrics")

        if not title or not metrics:
            return jsonify({"error": "Title and Metrics are required fields"}), 400

        grouped_metrics = _group_metrics(metrics)

        if not supabase:
             return jsonify({"error": "Database connection not established"}), 500

        response = supabase.table("job_requirements").insert({
            "title": title,
            "description": description,
            "metrics": grouped_metrics
        }).execute()

        return jsonify({"success": True, "data": response.data}), 201
    except Exception as e:
        print(f"ERROR saving job description: {str(e)}")
        return jsonify({"error": f"Failed to save to database: {str(e)}"}), 500

@job_descriptions_bp.route("/update-job-description/<id>", methods=["PUT"])
def update_job_description(id):
    """Overwrite an existing Job Description in Supabase"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description")
        metrics = data.get("metrics")

        if not title or not metrics:
            return jsonify({"error": "Title and Metrics are required fields"}), 400

        # Maintain grouped consistency
        grouped_metrics = _group_metrics(metrics)

        if not supabase:
             return jsonify({"error": "Database connection not established"}), 500

        response = supabase.table("job_requirements").update({
            "title": title,
            "description": description,
            "metrics": grouped_metrics
        }).eq("id", id).execute()

        return jsonify({"success": True, "data": response.data}), 200

    except Exception as e:
        print(f"ERROR updating job description: {str(e)}")
        return jsonify({"error": f"Failed to update database: {str(e)}"}), 500

@job_descriptions_bp.route("/delete-job-description/<id>", methods=["DELETE"])
def delete_job_description(id):
    """Permanently remove a Job Description from Supabase"""
    try:
        if not supabase:
             return jsonify({"error": "Database connection not established"}), 500

        response = supabase.table("job_requirements").delete().eq("id", id).execute()
        return jsonify({"success": True, "data": response.data}), 200

    except Exception as e:
        print(f"ERROR deleting job description: {str(e)}")
        return jsonify({"error": f"Failed to delete from database: {str(e)}"}), 500

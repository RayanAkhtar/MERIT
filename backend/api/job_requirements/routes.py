from flask import Blueprint, jsonify, request
from core.supabase import supabase

job_reqs_bp = Blueprint("job_requirements", __name__)

@job_reqs_bp.route("/save-cvs", methods=["POST"])
def save_cvs():
    """Attempt to save multiple CVs. Returns error as it's not implemented yet."""
    if 'files' not in request.files or not request.files.getlist('files'):
        return jsonify({"error": "No files provided"}), 400
    return jsonify({"error": "Saving CVs is not implemented yet."}), 501

@job_reqs_bp.route("/save-job-requirements", methods=["POST"])
def save_job_requirements():
    """Save finalized Job Requirements to Supabase"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description")
        metrics = data.get("metrics")

        if not title or not metrics:
            return jsonify({"error": "Title and Metrics are required fields"}), 400

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

        if not supabase:
             return jsonify({"error": "Database connection not established"}), 500

        response = supabase.table("job_requirements").insert({
            "title": title,
            "description": description,
            "metrics": grouped_metrics
        }).execute()

        return jsonify({"success": True, "data": response.data}), 201

    except Exception as e:
        print(f"ERROR saving job requirements: {str(e)}")
        return jsonify({"error": f"Failed to save to database: {str(e)}"}), 500

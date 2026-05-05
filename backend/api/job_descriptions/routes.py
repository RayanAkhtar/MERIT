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
    response = supabase.table("job_requirements").select("*").order("created_at", desc=True).execute()
    return jsonify(response.data), 200

def _group_metrics(metrics):
    """Internal helper to structure flat metric lists into category-based groups for Supabase storage."""
    # list_type_cats = ["Languages", "Technologies", "Soft Skills", "Responsibilities", "Requirements", "Education"]
    list_type_cats = ["Languages", "Technologies", "Education"]
    
    # Excluded categories (Soft Skills, Responsibilities, etc.) since they were never used, and just caused errors later down the line
    active_categories = ["Languages", "Technologies", "Education", "General"]
    
    grouped_metrics = {}
    for m in metrics:
        cat = m.get("category", "General")
        if cat not in active_categories:
            continue
            
        val = m.get("value", "")
        
        if cat not in grouped_metrics:
            cat_type = "list" if cat in list_type_cats else "key-value"
            grouped_metrics[cat] = {
                "type": cat_type,
                "value": []
            }
        
        if grouped_metrics[cat]["type"] == "list":
            if val: 
                if "suggested_weight" in m:
                    grouped_metrics[cat]["value"].append({
                        "value": val, 
                        "suggested_weight": m["suggested_weight"],
                        "suggested_weight_reasoning": m.get("suggested_weight_reasoning", ""),
                        "suggested_weight_math": m.get("suggested_weight_math", None)
                    })
                else:
                    grouped_metrics[cat]["value"].append(val)
        else:
            item = {k: v for k, v in m.items() if k != 'category'}
            grouped_metrics[cat]["value"].append(item)
    return grouped_metrics

@job_descriptions_bp.route("/save-job-description", methods=["POST"])
def save_job_description():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Handle both single object and list of objects
    if isinstance(data, list):
        results = []
        for item in data:
            title = item.get("title")
            description = item.get("description")
            metrics = item.get("metrics")

            if not title or not metrics:
                continue

            grouped_metrics = _group_metrics(metrics)
            response = supabase.table("job_requirements").insert({
                "title": title,
                "description": description,
                "metrics": grouped_metrics
            }).execute()
            results.append(response.data)
        return jsonify({"success": True, "data": results}), 201
    else:
        title = data.get("title")
        description = data.get("description")
        metrics = data.get("metrics")

        if not title or not metrics:
            return jsonify({"error": "Title and Metrics are required fields"}), 400

        grouped_metrics = _group_metrics(metrics)

        response = supabase.table("job_requirements").insert({
            "title": title,
            "description": description,
            "metrics": grouped_metrics
        }).execute()

        return jsonify({"success": True, "data": response.data}), 201

@job_descriptions_bp.route("/update-job-description/<id>", methods=["PUT"])
def update_job_description(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get("title")
    description = data.get("description")
    metrics = data.get("metrics")

    if not title or not metrics:
        return jsonify({"error": "Title and Metrics are required fields"}), 400

    grouped_metrics = _group_metrics(metrics)

    response = supabase.table("job_requirements").update({
        "title": title,
        "description": description,
        "metrics": grouped_metrics
    }).eq("id", id).execute()

    return jsonify({"success": True, "data": response.data}), 200

@job_descriptions_bp.route("/delete-job-description/<id>", methods=["DELETE"])
def delete_job_description(id):
    response = supabase.table("job_requirements").delete().eq("id", id).execute()
    return jsonify({"success": True, "data": response.data}), 200

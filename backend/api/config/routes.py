from flask import Blueprint, jsonify, request
from core.supabase import supabase

config_bp = Blueprint("config", __name__)

@config_bp.route("/create-config", methods=["POST"])
def create_config():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    job_id = data.get("job_id")
    batch_id = data.get("batch_id")
    weights = data.get("weights")
    active_metrics = data.get("active_metrics")

    if not name or not job_id or not batch_id or not weights:
        return jsonify({"error": "Missing required fields"}), 400

    response = supabase.table("matching_configs").insert({
        "name": name,
        "job_id": job_id,
        "batch_id": batch_id,
        "weights": weights,
        "active_metrics": active_metrics
    }).execute()

    return jsonify({"success": True, "data": response.data}), 201

@config_bp.route("/update-config/<config_id>", methods=["PUT"])
def update_config(config_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    job_id = data.get("job_id")
    batch_id = data.get("batch_id")
    weights = data.get("weights")
    active_metrics = data.get("active_metrics")

    update_payload = {}
    if name: update_payload["name"] = name
    if job_id: update_payload["job_id"] = job_id
    if batch_id: update_payload["batch_id"] = batch_id
    if weights: update_payload["weights"] = weights
    if active_metrics: update_payload["active_metrics"] = active_metrics

    response = supabase.table("matching_configs").update(update_payload).eq("id", config_id).execute()

    return jsonify({"success": True, "data": response.data}), 200

@config_bp.route("/get-configs", methods=["GET"])
def get_configs():
    response = supabase.table("matching_configs").select(
        "*, job_requirements(title, metrics), batch_data(batch_name, candidate_ids)"
    ).order("created_at", desc=True).execute()
    
    return jsonify(response.data), 200

@config_bp.route("/delete-config/<config_id>", methods=["DELETE"])
def delete_config(config_id):
    response = supabase.table("matching_configs").delete().eq("id", config_id).execute()
    return jsonify({"success": True, "data": response.data}), 200

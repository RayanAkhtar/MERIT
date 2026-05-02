from flask import Blueprint, jsonify
import os
import shutil
from core.supabase import supabase

system_bp = Blueprint("system", __name__)

@system_bp.route("/purge-database", methods=["POST"])
def purge_database():
    try:
        # first clear Database Tables
        # ordered to respect foreign key constraints and minimise deadlocks/timeouts
        tables = [
            "past_results",
            "matching_configs",
            "job_requirements",
            "batch_data",
            "candidate_education",
            "candidate_data",
            "linkedin_education",
            "linkedin_experience",
            "github_projects",
            "github_profiles",
            "linkedin_profiles"
        ]
        
        for table in tables:
            try:
                # using .neq filter trick for PostgREST
                supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            except Exception as table_err:
                print(f"Warning: Could not purge table {table}: {table_err}")
            
        # then clear supabase storage cvs bucket
        try:
            # list files in batches to avoid large payload errors
            storage = supabase.storage.from_('cvs')
            res = storage.list()
            if res:
                # filtering out system files or placeholders if any
                file_names = [f['name'] for f in res if f['name'] != '.emptyFolderPlaceholder']
                if file_names:
                    # remove files in a single call (or loop if it times out)
                    storage.remove(file_names)
        except Exception as e:
            print(f"Error clearing storage: {e}")

        return jsonify({"success": True, "message": "Database and storage purged successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@system_bp.route("/purge-cache", methods=["POST"])
def purge_cache():
    try:
        cache_dir = os.path.join(os.getcwd(), "cached")
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
            return jsonify({"success": True, "message": "Cache files purged successfully."}), 200
        else:
            return jsonify({"error": "Cache directory not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

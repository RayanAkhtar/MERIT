from core.parsers.update_skills import update_skills
from api import create_app


app = create_app()

from flask import send_from_directory
import os

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

if __name__ == "__main__":
    update_skills()
    app.run(debug=True)
